# 1C-Bitrix Aspro Digital 2.0 Design Tokens

Extracted from aks.group (live site analysis, 2026-05).

## CSS Custom Properties

Sources: `<style>` in `<head>`, plus aggregated from `template_*.css`.

```css
html {
  --theme-base-color: #2c6484;           /* Primary: dark steel blue */
  --theme-base-opacity-color: #2c64841a; /* 10% opacity version */
  --theme-more-color: #ec6a62;           /* Accent: coral/red */
  --theme-border-radius: 4px;
  --theme-text-transform: none;
  --theme-letter-spacing: normal;
  --theme-button-font-size: 0%;
  --theme-base-color-hue: 202;
  --theme-base-color-saturation: 50%;
  --theme-base-color-lightness: 35%;
  --theme-more-color-hue: 3;
  --theme-more-color-saturation: 78%;
  --theme-more-color-lightness: 65%;
  --theme-lightness-hover-diff: 6%;
}
```

## Body Classes (template markers)

```html
<body class="
  site_s1
  header_padding-122
  side_left
  hide_menu_page
  front_page
  region_confirm_top
  header_fill_colored
  all_title_2
  menu_lowercase_y
  fixed_y
  mfixed_n
  mfixed_view_always
  title_position_left
  mmenu_leftside
  mheader-v1
  footer-v2
  fill_bg_
  header-v4
  title-v2
  bottom-icons-panel_n
  with_order
  with_phones
  theme-light
">
```

Key markers:
- `front_page` = главная страница
- `header-v4`, `footer-v2`, `mheader-v1` = версии шаблонов в теме
- `theme-light` = светлая тема
- `fill_bg_` / `header_fill_colored` = цветная шапка

## Color Palette (top frequencies in CSS)

| Color | Usage |
|-------|-------|
| #9e9e9e | Grey (secondary text, borders) |
| #2c6484 | **Base brand** (nav, headers, primary buttons) |
| #e5e5e5 | Light grey (dividers, backgrounds) |
| #f2f2f2 | Near-white (section backgrounds) |
| #ec6a62 | **Accent** (CTAs, active states, hover) |
| #34759b | Base hover |
| #f8a132 | Warning/alert yellow |
| #39baec | Info blue |
| #9dca53 / #84bc29 | Success green |

## Typography

- **Primary font:** `'IBM Plex Sans', Arial, sans-serif`
- **Fallback:** `'Open Sans', Helvetica, Arial, sans-serif`
- **Base sizes:** 13px (body), 11-12px (small/meta), ~1.07-1.13em (h4-h6), ~1.27-1.47em (h2-h3)
- **Line heights:** default from Bootstrap

## Layout Grid

- Bootstrap-based (3/6/9/12 column grid)
- Max container width: ~1200px (Bootstrap default)
- Header padding: 122px (from `header_padding-122`)
- Border radius: 4px global

## Navigation Structure

```
[Логотип AKS.GROUP]  [выбор города]  [телефон]  [корзина]
  Продукты | Услуги | Кейсы | Компания
```

## Footer Sections

```
Контакты: телефон, email (ast@aks.group), адрес (Астрахань, ул Адмиралтейская д 14 к б оф 409)
Услуги: Автоматизация на iiko, Аудит и консалтинг, Wi-Fi, Видеонаблюдение, IT-поддержка, Обучение, ТС ПИОТ
Каталог: Готовые комплекты, Лицензии iiko, ККТ
Компания: О компании, История, Документы, Сертификаты, Партнеры, Клиенты, Сотрудники, Вакансии, Отзывы, Реквизиты
Информация: Вопрос-ответ, Оплата, Обзоры, Возможности
© 2026 Аспро: Digital 2.0 - Корпоративный сайт
```

## Template Meta

- **CMS:** 1C-Bitrix Site Manager (header: `X-Powered-CMS: Bitrix Site Manager`)
- **Template:** Aspro: Digital 2.0 — Корпоративный сайт (aspro-allcorp3digital)
- **jQuery:** 3.6.0
- **Icons:** FontAwesome
- **Carousel:** Owl Carousel
- **Scrollbar:** mCustomScrollbar
- **Modals:** jqModal
- **Lazy loading:** lazysizes + ls.unveilhooks

## Recovery Note

The Aspro template stores all theme customization in CSS variables in `<head>`. These override the compiled CSS. When recreating the design, prioritize these variables — they represent the ACTUAL customizations the site owner made, while the compiled CSS has all the Aspro defaults beneath.
