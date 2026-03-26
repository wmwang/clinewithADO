---
name: ppt-generation
description: Use this skill when the user requests to generate, create, or make presentations (PPT/PPTX). Creates visually rich slides by generating images for each slide and composing them into a PowerPoint file.
---

# PPT Generation Skill

## Overview

This skill generates professional PowerPoint presentations by creating AI-generated images for each slide and composing them into a PPTX file. The workflow includes planning the presentation structure with a consistent visual style, generating slide images sequentially (using the previous slide as a reference for style consistency), and assembling them into a final presentation.

## Core Capabilities

- Plan and structure multi-slide presentations with unified visual style
- Support multiple presentation styles: Business, Academic, Minimal, Apple Keynote, Creative
- Generate unique AI images for each slide using image-generation skill
- Maintain visual consistency by using previous slide as reference image
- Compose images into a professional PPTX file

## Presentation Styles

Choose one of the following styles when creating the presentation plan:

| Style | Description | Best For |
|-------|-------------|----------|
| **glassmorphism** | Frosted glass panels with blur effects, floating translucent cards, vibrant gradient backgrounds, depth through layering | Tech products, AI/SaaS demos, futuristic pitches |
| **dark-premium** | Rich black backgrounds (#0a0a0a), luminous accent colors, subtle glow effects, luxury brand aesthetic | Premium products, executive presentations, high-end brands |
| **gradient-modern** | Bold mesh gradients, fluid color transitions, contemporary typography, vibrant yet sophisticated | Startups, creative agencies, brand launches |
| **neo-brutalist** | Raw bold typography, high contrast, intentional "ugly" aesthetic, anti-design as design, Memphis-inspired | Edgy brands, Gen-Z targeting, disruptive startups |
| **3d-isometric** | Clean isometric illustrations, floating 3D elements, soft shadows, tech-forward aesthetic | Tech explainers, product features, SaaS presentations |
| **editorial** | Magazine-quality layouts, sophisticated typography hierarchy, dramatic photography, Vogue/Bloomberg aesthetic | Annual reports, luxury brands, thought leadership |
| **minimal-swiss** | Grid-based precision, Helvetica-inspired typography, bold use of negative space, timeless modernism | Architecture, design firms, premium consulting |
| **keynote** | Apple-inspired aesthetic with bold typography, dramatic imagery, high contrast, cinematic feel | Keynotes, product reveals, inspirational talks |

## Workflow

### Step 1: Understand Requirements

When a user requests presentation generation, identify:

- Topic/subject: What is the presentation about
- Number of slides: How many slides are needed (default: 5-10)
- **Style**: business / academic / minimal / keynote / creative
- Aspect ratio: Standard (16:9) or classic (4:3)
- Content outline: Key points for each slide

### Step 2: Create Presentation Plan

Create a JSON file in the workspace with the presentation structure. **Important**: Include the `style` field to define the overall visual consistency.

```json
{
  "title": "Presentation Title",
  "style": "keynote",
  "style_guidelines": {
    "color_palette": "Deep black backgrounds, white text, single accent color (blue or orange)",
    "typography": "Bold sans-serif headlines, clean body text, dramatic size contrast",
    "imagery": "High-quality photography, full-bleed images, cinematic composition",
    "layout": "Generous whitespace, centered focus, minimal elements per slide"
  },
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "Main Title",
      "subtitle": "Subtitle or tagline",
      "visual_description": "Detailed description for image generation"
    },
    {
      "slide_number": 2,
      "type": "content",
      "title": "Slide Title",
      "key_points": ["Point 1", "Point 2", "Point 3"],
      "visual_description": "Detailed description for image generation"
    }
  ]
}
```

### Step 3: Generate Slide Images Sequentially

**IMPORTANT**: Generate slides **strictly one by one, in order**. Do NOT parallelize or batch image generation. Each slide depends on the previous slide's output as a reference image. Generating slides in parallel will break visual consistency and is not allowed.

1. Read the image-generation skill: `Skills/image-generation/SKILL.md`

2. **For the FIRST slide (slide 1)**, create a prompt that establishes the visual style:

```json
{
  "prompt": "Professional presentation slide. [style_guidelines from plan]. Title: 'Your Title'. [visual_description]. This slide establishes the visual language for the entire presentation.",
  "style": "[Based on chosen style - e.g., Apple Keynote aesthetic, dramatic lighting, cinematic]",
  "composition": "Clean layout with clear text hierarchy, [style-specific composition]",
  "color_palette": "[From style_guidelines]",
  "typography": "[From style_guidelines]"
}
```

3. **For subsequent slides (slide 2+)**, use the PREVIOUS slide as a reference image:

```json
{
  "prompt": "Professional presentation slide continuing the visual style from the reference image. Maintain the same color palette, typography style, and overall aesthetic. Title: 'Slide Title'. [visual_description]. Keep visual consistency with the reference.",
  "style": "Match the style of the reference image exactly",
  "composition": "Similar layout principles as reference, adapted for this content",
  "color_palette": "Same as reference image",
  "consistency_note": "This slide must look like it belongs in the same presentation as the reference image"
}
```

4. **Continue for all remaining slides**, always referencing the previous slide.

### Step 4: Compose PPT

After all slide images are generated, call the composition script:

```bash
python Skills/ppt-generation/scripts/generate.py \
  --plan-file <path-to-presentation-plan.json> \
  --slide-images <path-to-slide-01.jpg> <path-to-slide-02.jpg> <path-to-slide-03.jpg> \
  --output-file <path-to-output.pptx>
```

Parameters:

- `--plan-file`: Absolute path to the presentation plan JSON file (required)
- `--slide-images`: Absolute paths to slide images in order (required, space-separated)
- `--output-file`: Absolute path to output PPTX file (required)

> **Note**: Do NOT read the python file, just call it with the parameters.

## Complete Example: Glassmorphism Style

User request: "Create a presentation about AI product launch"

### Step 1: Create presentation plan

Create a `presentation-plan.json` file:
```json
{
  "title": "Introducing Nova AI",
  "style": "glassmorphism",
  "style_guidelines": {
    "color_palette": "Vibrant purple-to-cyan gradient background (#667eea→#00d4ff), frosted glass panels with 15-20% white opacity, electric accents",
    "typography": "SF Pro Display style, bold 700 weight white titles with subtle text-shadow, clean 400 weight body text, excellent contrast on glass",
    "imagery": "Abstract 3D glass spheres, floating translucent geometric shapes, soft luminous orbs, depth through layered transparency",
    "layout": "Centered frosted glass cards with 32px rounded corners, 48-64px padding, floating above gradient, layered depth with soft shadows",
    "effects": "Backdrop blur 20-40px on glass panels, subtle white border glow, soft colored shadows matching gradient, light refraction effects",
    "visual_language": "Apple Vision Pro / visionOS aesthetic, premium depth through transparency, futuristic yet approachable, 2024 design trends"
  },
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "Introducing Nova AI",
      "subtitle": "Intelligence, Reimagined",
      "visual_description": "Stunning gradient background flowing from deep purple (#667eea) through magenta to cyan (#00d4ff). Center: large frosted glass panel with strong backdrop blur, containing bold white title 'Introducing Nova AI' and lighter subtitle. Floating 3D glass spheres and abstract shapes around the card creating depth. Soft glow emanating from behind the glass panel. Premium visionOS aesthetic."
    },
    {
      "slide_number": 2,
      "type": "content",
      "title": "Why Nova?",
      "key_points": ["10x faster processing", "Human-like understanding", "Enterprise-grade security"],
      "visual_description": "Same purple-cyan gradient background. Left side: floating frosted glass card with title 'Why Nova?' in bold white, three key points below with subtle glass pill badges. Right side: abstract 3D visualization of neural network as interconnected glass nodes with soft glow. Floating translucent geometric shapes adding depth."
    },
    {
      "slide_number": 3,
      "type": "content",
      "title": "How It Works",
      "key_points": ["Natural language input", "Multi-modal processing", "Instant insights"],
      "visual_description": "Gradient background consistent with previous slides. Central composition: three stacked frosted glass cards at slight angles showing the workflow steps, connected by soft glowing lines. Each card has an abstract icon. Floating glass orbs and light particles around the composition."
    }
  ]
}
```

### Step 2: Read image-generation skill

Read `Skills/image-generation/SKILL.md` to understand how to generate images.

### Step 3: Generate slide images sequentially with reference chaining

**Slide 1 - Title (establishes the visual language):**

Create a `slide-01-prompt.json`:
```json
{
  "prompt": "Ultra-premium presentation title slide with glassmorphism design. Background: smooth flowing gradient from deep purple (#667eea) through magenta to cyan (#00d4ff). Center: large frosted glass panel with strong backdrop blur, rounded corners 32px, containing bold white sans-serif title 'Introducing Nova AI' and subtitle 'Intelligence, Reimagined'. Floating 3D glass spheres and geometric shapes creating depth. Apple Vision Pro / visionOS UI aesthetic. 16:9 aspect ratio.",
  "style": "Glassmorphism, visionOS aesthetic, premium tech, 2024 design trends",
  "composition": "Centered glass card as focal point, floating 3D elements creating depth at edges",
  "color_palette": "Purple gradient #667eea, magenta #f093fb, cyan #00d4ff, frosted white rgba(255,255,255,0.15)"
}
```

**Slide 2 - Content (MUST reference slide 1 for consistency):**

Create a `slide-02-prompt.json`:
```json
{
  "prompt": "Presentation slide continuing EXACT visual style from reference image. SAME purple-to-cyan gradient background, SAME glassmorphism aesthetic. Left: frosted glass card with title 'Why Nova?' and three feature points. Right: abstract 3D neural network visualization. CRITICAL: This slide must match the reference image exactly.",
  "style": "MATCH REFERENCE EXACTLY - Glassmorphism, visionOS aesthetic",
  "color_palette": "EXACTLY match reference: purple #667eea, cyan #00d4ff gradient",
  "consistency_note": "Must be visually identical in style to reference image."
}
```

**Continue for all remaining slides**, each referencing the previous slide.

### Step 4: Compose final PPT

```bash
python Skills/ppt-generation/scripts/generate.py \
  --plan-file presentation-plan.json \
  --slide-images slide-01.jpg slide-02.jpg slide-03.jpg \
  --output-file nova-presentation.pptx
```

## Style-Specific Guidelines

### Glassmorphism Style
```json
{
  "style": "glassmorphism",
  "style_guidelines": {
    "color_palette": "Vibrant gradient backgrounds (purple #667eea to pink #f093fb, or cyan #4facfe to blue #00f2fe), frosted white panels with 20% opacity",
    "typography": "SF Pro Display or Inter font style, bold 600-700 weight titles, clean 400 weight body, white text with subtle drop shadow",
    "imagery": "Abstract 3D shapes floating in space, soft blurred orbs, geometric primitives with glass material",
    "layout": "Floating card panels with backdrop-blur effect, generous padding (48-64px), rounded corners (24-32px radius)",
    "effects": "Frosted glass blur (backdrop-filter: blur 20px), subtle white border (1px rgba 255,255,255,0.2), soft glow behind panels"
  }
}
```

### Dark Premium Style
```json
{
  "style": "dark-premium",
  "style_guidelines": {
    "color_palette": "Deep black base (#0a0a0a to #121212), luminous accent color (electric blue #00d4ff, neon purple #bf5af2, or gold #ffd700)",
    "typography": "Elegant sans-serif, dramatic size contrast (72pt+ headlines, 18pt body), pure white (#ffffff) text",
    "imagery": "Dramatic studio lighting, rim lights and edge glow, cinematic product shots",
    "layout": "Generous negative space (60%+), asymmetric balance, single focal point per slide",
    "effects": "Subtle ambient glow behind key elements, light bloom effects, grain texture overlay (2-3% opacity)"
  }
}
```

### Gradient Modern Style
```json
{
  "style": "gradient-modern",
  "style_guidelines": {
    "color_palette": "Bold mesh gradients (Stripe/Linear style: purple-pink-orange #7c3aed→#ec4899→#f97316)",
    "typography": "Modern geometric sans-serif, oversized bold headlines (80pt+), comfortable body text (20pt)",
    "imagery": "Abstract fluid shapes, morphing gradients, 3D rendered abstract objects",
    "layout": "Dynamic asymmetric compositions, overlapping elements with blend modes",
    "effects": "Smooth gradient transitions, subtle noise texture (3-5% for depth)"
  }
}
```

### Neo-Brutalist Style
```json
{
  "style": "neo-brutalist",
  "style_guidelines": {
    "color_palette": "High contrast primaries: stark black, pure white, with bold accent (hot pink #ff0080, electric yellow #ffff00)",
    "typography": "Ultra-bold condensed type (Impact, Druk, or Bebas Neue style), UPPERCASE headlines, extreme size contrast",
    "imagery": "Raw unfiltered photography, intentional visual noise, halftone patterns, cut-out collage aesthetic",
    "layout": "Broken grid, overlapping elements, thick black borders (4-8px)",
    "effects": "Hard shadows (no blur, offset 8-12px), pixelation accents, scan lines"
  }
}
```

### 3D Isometric Style
```json
{
  "style": "3d-isometric",
  "style_guidelines": {
    "color_palette": "Soft contemporary palette: muted purples (#8b5cf6), teals (#14b8a6), warm corals (#fb7185), with cream or light gray backgrounds (#fafafa)",
    "typography": "Friendly geometric sans-serif (Circular, Gilroy, or Quicksand style), medium weight headlines",
    "imagery": "Clean isometric 3D illustrations, consistent 30° isometric angle, soft clay-render aesthetic",
    "layout": "Central isometric scene as hero, text balanced around 3D elements",
    "effects": "Soft drop shadows (20px blur, 30% opacity), ambient occlusion on 3D objects"
  }
}
```

### Editorial Style
```json
{
  "style": "editorial",
  "style_guidelines": {
    "color_palette": "Sophisticated neutrals: off-white (#f5f5f0), charcoal (#2d2d2d), with single accent color (burgundy #7c2d12, forest #14532d, or navy #1e3a5f)",
    "typography": "Refined serif for headlines (Playfair Display style), clean sans-serif for body, dramatic size hierarchy (96pt headlines)",
    "imagery": "Magazine-quality photography, dramatic crops, full-bleed images (Vogue, Bloomberg style)",
    "layout": "Sophisticated grid system, intentional asymmetry, pull quotes as design elements",
    "effects": "Minimal effects - let photography and typography shine, elegant borders and rules"
  }
}
```

### Minimal Swiss Style
```json
{
  "style": "minimal-swiss",
  "style_guidelines": {
    "color_palette": "Pure white (#ffffff) or off-white (#fafaf9) backgrounds, true black (#000000) text, single bold accent (Swiss red #ff0000, Klein blue #002fa7)",
    "typography": "Helvetica Neue or Aktiv Grotesk, strict type scale (12/16/24/48/96), flush-left ragged-right alignment",
    "imagery": "Objective photography, geometric shapes, clean iconography, mathematical precision",
    "layout": "Strict grid adherence, modular compositions, generous whitespace (40%+ of slide)",
    "effects": "None - purity of form, no shadows, no gradients, no decorative elements"
  }
}
```

### Keynote Style (Apple Style)
```json
{
  "style": "keynote",
  "style_guidelines": {
    "color_palette": "Deep blacks (#000000 to #1d1d1f), pure white text, signature blue (#0071e3) or gradient accents",
    "typography": "San Francisco Pro Display, extreme weight contrast (bold 80pt+ titles, light 24pt body), negative letter-spacing on headlines",
    "imagery": "Cinematic photography, shallow depth of field, dramatic lighting, product hero shots",
    "layout": "Maximum negative space, single powerful image or statement per slide, no clutter",
    "effects": "Subtle gradient overlays, light bloom and glow on key elements, reflection on surfaces"
  }
}
```

## Dependencies

This skill requires:
- **Python packages**: `python-pptx`, `Pillow` — install with `pip install python-pptx Pillow`
- **image-generation skill** (`Skills/image-generation/`): used to generate slide images

## Notes

### Critical Quality Guidelines

**Prompt Engineering for Professional Results:**
- Always use English for image prompts regardless of user's language
- Be EXTREMELY specific about visual details - vague prompts produce generic results
- Include exact hex color codes (e.g., #667eea not "purple")
- Specify typography details: font weight (400/700), size hierarchy, letter-spacing
- Reference real design systems: "visionOS aesthetic", "Stripe website style", "Bloomberg Businessweek layout"

**Visual Consistency (Most Important):**
- **Generate slides sequentially** - each slide MUST reference the previous one
- The first slide is critical - it establishes the visual language for the entire presentation
- In every subsequent slide prompt, explicitly state: "continuing EXACT visual style from reference image"
- Use SAME, EXACT, MATCH keywords emphatically in prompts to enforce consistency
- Include a `consistency_note` field in every JSON prompt after slide 1
- If a slide looks inconsistent, regenerate it with STRONGER reference emphasis

**Design Principles for Modern Aesthetics:**
- Embrace negative space - 40-60% empty space creates premium feel
- Limit elements per slide - one focal point, one message
- Use depth through layering (shadows, transparency, z-depth)
- Typography hierarchy: massive headlines (72pt+), comfortable body (18-24pt)
- Color restraint: one primary palette, 1-2 accent colors maximum

**Common Mistakes to Avoid:**
- ❌ Generic prompts like "professional slide" - be specific
- ❌ Too many elements/text per slide - cluttered = unprofessional
- ❌ Inconsistent colors between slides - always reference previous slide
- ❌ Skipping the reference image parameter - this breaks visual consistency
- ❌ Using different design styles within one presentation
- ❌ Generating slides in parallel - slides MUST be generated one at a time in order (slide 1 → 2 → 3 ...), never concurrently

**Recommended Styles for Different Contexts:**
- Tech product launch → `glassmorphism` or `gradient-modern`
- Luxury/premium brand → `dark-premium` or `editorial`
- Startup pitch → `gradient-modern` or `minimal-swiss`
- Executive presentation → `dark-premium` or `keynote`
- Creative agency → `neo-brutalist` or `gradient-modern`
- Data/analytics → `minimal-swiss` or `3d-isometric`
