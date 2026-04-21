# Sosa Tech Solutions — Landing Page

Miami-based tech consulting landing page. Bilingual (EN/ES), SEO-optimized, with Facebook Pixel, WhatsApp CTA, and GSAP animations.

**Slogan:** We build. You grow.

---

## 📁 File Structure

```
sosatech-landing/
├── index.html                    # Main landing page
├── favicon.ico                   # Legacy browser favicon (16+32px embedded)
├── robots.txt                    # Search engine crawler rules
├── sitemap.xml                   # Sitemap for Google Search Console
├── og-image.png                  # Social sharing preview (1200x630)
├── README.md                     # This file
└── assets/
    ├── logo-dark.png             # Logo for dark backgrounds
    ├── logo-light.png            # Logo for light backgrounds
    ├── logo.svg                  # Scalable vector logo
    ├── whatsapp-profile-icon.png # Source logo mark (640x640)
    ├── favicon-16x16.png         # Browser tab
    ├── favicon-32x32.png         # Browser tab (retina)
    ├── favicon-180x180.png       # iOS Apple Touch Icon
    ├── favicon-192x192.png       # Android PWA
    └── favicon-512x512.png       # Android PWA splash
```

---

## 🚀 Deployment

### Option 1: GitHub Pages (Free)

```bash
git init
git add .
git commit -m "Initial launch"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sosatech-landing.git
git push -u origin main
```

Then go to **Settings → Pages → Source: main branch → root** to enable.

### Option 2: Your VPS

Upload all files to your web root (e.g., `/var/www/sosatech.io/`) and make sure `index.html` is the default document.

---

## ⚙️ Before Going Live — Checklist

### 1. Replace Facebook Pixel ID
In `index.html`, find and replace both instances:
```
REPLACE_WITH_YOUR_PIXEL_ID
```
Get your Pixel ID from: https://business.facebook.com/events_manager

### 2. Activate the Contact Form (Web3Forms)
The form POSTs to [web3forms.com](https://web3forms.com) and delivers submissions to `info@sosatechsolutions.com`.

**One-time setup:**
1. Go to https://web3forms.com
2. Enter `info@sosatechsolutions.com` → click "Create Access Key"
3. In `index.html` replace the placeholder:
```html
<input type="hidden" name="access_key" value="YOUR_WEB3FORMS_KEY"/>
```

**Spam & bot protection included:**
- Honeypot field (hidden checkbox — bots trigger it, submissions are silently dropped)
- Time check (rejects submissions under 3 seconds — bot speed)
- Double-submit guard (button disabled after first click)
- Client-side validation (name, email, message required)
- Server-side spam filtering by Web3Forms

### 3. Update URLs
In `index.html` and `sitemap.xml`, replace `https://sosatech.io/` with your actual domain if different.

### 4. Favicon ✅
Already wired. All sizes generated from `assets/whatsapp-profile-icon.png` and linked in `<head>`.

---

## 🔍 Post-Launch SEO Setup

1. **Google Search Console** — https://search.google.com/search-console
   - Add property: `sosatech.io`
   - Submit sitemap: `https://sosatech.io/sitemap.xml`

2. **Google Business Profile** — https://business.google.com
   - Create listing for Miami location (local SEO)

3. **Facebook Business Page** — link the Pixel to your page

4. **Test social previews:**
   - Facebook: https://developers.facebook.com/tools/debug
   - LinkedIn: https://www.linkedin.com/post-inspector
   - General: https://opengraph.xyz

---

## 📱 Contact Info (Hard-coded in site)

- **WhatsApp:** +1 (305) 741-5702
- **Email:** info@sosatechsolutions.com

---

## 🛠️ Tech Stack

- Pure HTML/CSS/JS (no build step needed)
- GSAP + ScrollTrigger for animations
- Google Fonts: Syne, DM Mono, DM Sans
- Facebook Pixel
- JSON-LD schema (LocalBusiness)

---

© 2026 Sosa Tech Solutions · Miami, FL
