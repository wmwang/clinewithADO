#!/usr/bin/env python3
"""
md_to_html.py — 合併多個 Markdown 檔案並輸出帶樣式的 HTML
用途：將 legacy-code-analyzer 產出的 md 報告合併為 KB 上傳用 HTML

用法：
  python3 md_to_html.py 05-ui-and-form-behavior.md 06-java-ca-api-spec.md \
      --output OMVP820-report.html --title "OMVP820 功能分析報告"
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Markdown → HTML 轉換（純標準函式庫，無需 pip install）
# ---------------------------------------------------------------------------

def md_to_html_body(text: str) -> str:
    """簡易 Markdown 轉 HTML，涵蓋常用語法。"""
    lines = text.split('\n')
    html_lines = []
    i = 0
    in_code = False
    code_lang = ''
    code_buf = []
    in_table = False
    table_buf = []

    def flush_table():
        nonlocal in_table, table_buf
        if not table_buf:
            return ''
        rows = table_buf
        table_buf = []
        in_table = False
        out = ['<table>']
        for r_idx, row in enumerate(rows):
            cells = [c.strip() for c in row.strip('|').split('|')]
            # skip separator row (---|---)
            if all(re.fullmatch(r':?-+:?', c.strip()) for c in cells if c.strip()):
                continue
            tag = 'th' if r_idx == 0 else 'td'
            out.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>')
        out.append('</table>')
        return '\n'.join(out)

    def inline(s: str) -> str:
        """處理行內語法：bold、italic、code、link。"""
        # code `...`
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        # bold **...**
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        # italic *...*
        s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
        # link [text](url)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
        return s

    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.startswith('```'):
            if not in_code:
                in_code = True
                code_lang = line[3:].strip()
                code_buf = []
            else:
                in_code = False
                lang_cls = f' class="language-{code_lang}"' if code_lang else ''
                code_content = '\n'.join(code_buf).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_lines.append(f'<pre><code{lang_cls}>{code_content}</code></pre>')
                code_buf = []
                code_lang = ''
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # table row
        if line.startswith('|'):
            if not in_table:
                in_table = True
            table_buf.append(line)
            i += 1
            # peek: if next line is not a table row, flush
            if i >= len(lines) or not lines[i].startswith('|'):
                html_lines.append(flush_table())
            continue

        # if we were in a table and hit a non-table line
        if in_table:
            html_lines.append(flush_table())

        # headings
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            text_content = m.group(2).strip()
            anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', text_content.replace(' ', '-'))
            html_lines.append(f'<h{level} id="{anchor}">{inline(text_content)}</h{level}>')
            i += 1
            continue

        # blockquote
        if line.startswith('> '):
            html_lines.append(f'<blockquote><p>{inline(line[2:])}</p></blockquote>')
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r'-{3,}', line.strip()):
            html_lines.append('<hr>')
            i += 1
            continue

        # unordered list item
        if re.match(r'^(\s*[-*+])\s+', line):
            items = []
            ul_pat = re.compile(r'^\s*[-*+]\s+')
            while i < len(lines) and ul_pat.match(lines[i]):
                content = ul_pat.sub('', lines[i])
                items.append('<li>' + inline(content) + '</li>')
                i += 1
            html_lines.append('<ul>' + ''.join(items) + '</ul>')
            continue

        # ordered list item
        if re.match(r'^\s*\d+\.\s+', line):
            items = []
            ol_pat = re.compile(r'^\s*\d+\.\s+')
            while i < len(lines) and ol_pat.match(lines[i]):
                content = ol_pat.sub('', lines[i])
                items.append('<li>' + inline(content) + '</li>')
                i += 1
            html_lines.append('<ol>' + ''.join(items) + '</ol>')
            continue

        # blank line
        if line.strip() == '':
            html_lines.append('')
            i += 1
            continue

        # paragraph
        html_lines.append(f'<p>{inline(line)}</p>')
        i += 1

    return '\n'.join(html_lines)


# ---------------------------------------------------------------------------
# TOC 產生
# ---------------------------------------------------------------------------

def build_toc(html_body: str) -> str:
    headings = re.findall(r'<h([23])\s+id="([^"]+)">([^<]+(?:<[^>]+>[^<]*</[^>]+>)*[^<]*)</h\1>', html_body)
    if not headings:
        return ''
    toc = ['<nav id="toc"><h2>目錄</h2><ul>']
    for level, anchor, text in headings:
        indent = '  ' if level == '3' else ''
        clean_text = re.sub(r'<[^>]+>', '', text)
        toc.append(f'{indent}<li><a href="#{anchor}">{clean_text}</a></li>')
    toc.append('</ul></nav>')
    return '\n'.join(toc)


# ---------------------------------------------------------------------------
# HTML 樣板
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{
    font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    font-size: 15px;
    line-height: 1.7;
    color: #1a1a1a;
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px 32px;
    background: #fafafa;
  }}
  h1 {{ font-size: 1.9em; border-bottom: 3px solid #2563eb; padding-bottom: 8px; color: #1e3a8a; }}
  h2 {{ font-size: 1.4em; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-top: 2em; color: #1e40af; }}
  h3 {{ font-size: 1.15em; color: #1d4ed8; margin-top: 1.5em; }}
  h4 {{ font-size: 1em; color: #374151; }}
  nav#toc {{
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 16px 24px;
    margin-bottom: 32px;
    display: inline-block;
    min-width: 260px;
  }}
  nav#toc h2 {{ font-size: 1em; margin: 0 0 8px 0; border: none; color: #1e40af; }}
  nav#toc ul {{ margin: 0; padding-left: 16px; }}
  nav#toc li {{ margin: 3px 0; }}
  nav#toc a {{ color: #2563eb; text-decoration: none; }}
  nav#toc a:hover {{ text-decoration: underline; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 0.92em;
  }}
  th, td {{
    border: 1px solid #e2e8f0;
    padding: 8px 12px;
    text-align: left;
  }}
  th {{
    background: #e0f2fe;
    font-weight: 600;
    color: #0c4a6e;
  }}
  tr:nth-child(even) td {{ background: #f8fafc; }}
  code {{
    background: #f1f5f9;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 0.88em;
    color: #b91c1c;
  }}
  pre {{
    background: #1e293b;
    color: #e2e8f0;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 0.88em;
    line-height: 1.5;
    margin: 16px 0;
  }}
  pre code {{
    background: none;
    color: inherit;
    padding: 0;
    font-size: inherit;
  }}
  blockquote {{
    border-left: 4px solid #f59e0b;
    background: #fffbeb;
    margin: 12px 0;
    padding: 10px 16px;
    border-radius: 0 6px 6px 0;
    color: #78350f;
  }}
  blockquote p {{ margin: 0; }}
  hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 32px 0; }}
  section.part {{
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 24px 32px;
    margin-bottom: 32px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  .report-meta {{
    font-size: 0.82em;
    color: #6b7280;
    margin-bottom: 24px;
  }}
  strong {{ color: #111; }}
</style>
</head>
<body>

<h1>{title}</h1>
<p class="report-meta">產出時間：{generated_at}　｜　由 legacy-code-analyzer skill 自動產出</p>

{toc}

{sections}

</body>
</html>
"""

SECTION_LABELS = [
    "Form 分析（UI 說明）",
    "Java Clean Architecture API 規格",
]


# ---------------------------------------------------------------------------
# 主程式
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='合併 Markdown 報告為 HTML')
    parser.add_argument('inputs', nargs='+', help='輸入 Markdown 檔案（依序合併）')
    parser.add_argument('--output', '-o', required=True, help='輸出 HTML 路徑')
    parser.add_argument('--title', '-t', default='Legacy Code 分析報告', help='HTML 標題')
    args = parser.parse_args()

    sections_html = []
    combined_body = ''

    for idx, md_path in enumerate(args.inputs):
        p = Path(md_path)
        if not p.exists():
            print(f'[警告] 找不到檔案：{md_path}，跳過', file=sys.stderr)
            continue
        md_text = p.read_text(encoding='utf-8')
        body = md_to_html_body(md_text)
        label = SECTION_LABELS[idx] if idx < len(SECTION_LABELS) else p.stem
        section = f'<section class="part">\n<h2>{label}</h2>\n{body}\n</section>'
        sections_html.append(section)
        combined_body += body + '\n'

    toc = build_toc(combined_body)
    output = HTML_TEMPLATE.format(
        title=args.title,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M'),
        toc=toc,
        sections='\n\n'.join(sections_html),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding='utf-8')
    print(f'✅ HTML 報告已輸出：{out_path}')


if __name__ == '__main__':
    main()
