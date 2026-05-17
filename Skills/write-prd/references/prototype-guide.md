# 原型生成指南

## 技術規格

生成單檔案 HTML 原型，可直接在瀏覽器開啟：

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[產品名稱] - 原型</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* 自定義樣式 */
    </style>
</head>
<body>
    <!-- 頁面內容 -->
    <script>
        // 互動邏輯
    </script>
</body>
</html>
```

## 設計風格選項

### 1. Glassmorphism（毛玻璃）
- 半透明背景 + 模糊效果
- `backdrop-blur-lg bg-white/30`

### 2. Minimalism（極簡）
- 大量留白 + 清晰層次
- 黑白灰為主 + 單色點綴

### 3. Material Design
- 卡片陰影 + 圓角
- `shadow-md rounded-lg`

### 4. Dark Mode（深色模式）
- 深色背景 + 亮色文字
- `bg-gray-900 text-white`

## 必備互動元件

### 1. 導航欄
```html
<nav class="fixed top-0 w-full bg-white shadow-sm z-50">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div class="font-bold text-xl">Logo</div>
        <div class="flex gap-4">
            <a href="#" class="hover:text-blue-600">首頁</a>
            <a href="#" class="hover:text-blue-600">功能</a>
        </div>
    </div>
</nav>
```

### 2. 表單校驗
```javascript
function validateForm() {
    const input = document.getElementById('phone');
    const error = document.getElementById('error');
    if (!/^09\d{8}$/.test(input.value)) {
        error.textContent = '請輸入正確的手機號碼';
        error.classList.remove('hidden');
        return false;
    }
    error.classList.add('hidden');
    return true;
}
```

### 3. Loading 狀態
```javascript
function submitWithLoading(btn) {
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<svg class="animate-spin h-5 w-5 mr-2 inline" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" opacity="0.25"></circle><path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>提交中...';

    setTimeout(() => {
        btn.disabled = false;
        btn.textContent = originalText;
    }, 2000);
}
```

### 4. Toast 提示
```javascript
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg text-white ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} transition-opacity duration-300`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
```

### 5. 彈窗/抽屜
```html
<!-- 彈窗 -->
<div id="modal" class="fixed inset-0 bg-black/50 hidden items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-bold mb-4">標題</h3>
        <p>內容</p>
        <button onclick="closeModal()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded">關閉</button>
    </div>
</div>
```

### 6. Tab 頁面切換
```javascript
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('border-blue-600', 'text-blue-600'));
    document.getElementById(tabId).classList.remove('hidden');
    event.target.classList.add('border-blue-600', 'text-blue-600');
}
```

## 響應式適配

```html
<!-- 移動端漢堡選單 -->
<button class="md:hidden" onclick="toggleMenu()">
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
    </svg>
</button>

<!-- 響應式網格 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- 卡片 -->
</div>
```

## 模擬數據

```javascript
const mockData = {
    users: [
        { id: 1, name: '張三', phone: '0912345678', status: '正常' },
        { id: 2, name: '李四', phone: '0923456789', status: '停用' },
    ],
    orders: [
        { id: 'ORD001', amount: 299, status: '待支付', time: '2024-01-15 10:30' },
        { id: 'ORD002', amount: 599, status: '已完成', time: '2024-01-14 15:20' },
    ]
};
```