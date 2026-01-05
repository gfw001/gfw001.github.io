#!/usr/bin/env python3
"""
小红书图文生成器 - Xiaohongshu Card Generator
专业简洁风格 - Professional & Clean Style
"""

import sys
import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

# Configuration
CARD_SIZE = 1080
PADDING = 70
TITLE_FONT_SIZE = 52
BODY_FONT_SIZE = 26
LABEL_FONT_SIZE = 22
LINE_SPACING = 1.7
WATERMARK_TEXT = "pengandy.com"

# Professional color schemes - 专业简洁配色
COLOR_SCHEMES = [
    {
        'name': 'minimal_white',
        'bg': (255, 255, 255),           # 纯白
        'title': (26, 26, 26),           # 深黑
        'body': (80, 80, 80),            # 中灰
        'accent': (255, 107, 107),       # 活力红
        'tag_bg': (255, 245, 245),       # 浅红背景
    },
    {
        'name': 'soft_blue',
        'bg': (250, 252, 255),           # 浅蓝白
        'title': (30, 58, 138),          # 深蓝
        'body': (71, 85, 105),           # 蓝灰
        'accent': (59, 130, 246),        # 亮蓝
        'tag_bg': (239, 246, 255),       # 浅蓝背景
    },
    {
        'name': 'warm_cream',
        'bg': (255, 251, 245),           # 米白
        'title': (120, 53, 15),          # 棕色
        'body': (87, 83, 78),            # 暖灰
        'accent': (234, 88, 12),         # 橙色
        'tag_bg': (255, 247, 237),       # 浅橙背景
    },
    {
        'name': 'fresh_mint',
        'bg': (247, 254, 250),           # 薄荷白
        'title': (6, 78, 59),            # 深绿
        'body': (75, 85, 99),            # 冷灰
        'accent': (16, 185, 129),        # 翠绿
        'tag_bg': (236, 253, 245),       # 浅绿背景
    },
]

def parse_html(html_file):
    """Extract H2/H3 headings and their content"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    cards = []

    headings = soup.find_all(['h2', 'h3'])

    for heading in headings:
        title = heading.get_text().strip()
        content = []

        for sibling in heading.find_next_siblings():
            if sibling.name in ['h2', 'h3']:
                break
            if sibling.name == 'p':
                text = sibling.get_text().strip()
                if text:
                    content.append(text)
            elif sibling.name in ['ul', 'ol']:
                for li in sibling.find_all('li'):
                    text = li.get_text().strip()
                    if text:
                        content.append('• ' + text)

        if content:
            cards.append({
                'title': title,
                'content': '\n\n'.join(content[:6])  # Max 6 paragraphs
            })

    return cards

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width"""
    lines = []
    paragraphs = text.split('\n')

    for paragraph in paragraphs:
        if not paragraph.strip():
            continue

        words = paragraph.split()
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
            except:
                line_width = len(test_line) * 15

            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)

        if current_line:
            lines.append(' '.join(current_line))

    return lines

def generate_card_image(card, output_path, card_index, total_cards):
    """Generate professional Xiaohongshu-style card"""

    # Choose color scheme
    scheme = COLOR_SCHEMES[card_index % len(COLOR_SCHEMES)]

    # Create base image
    img = Image.new('RGB', (CARD_SIZE, CARD_SIZE), scheme['bg'])
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font = None
    body_font = None

    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                title_font = ImageFont.truetype(font_path, TITLE_FONT_SIZE)
                body_font = ImageFont.truetype(font_path, BODY_FONT_SIZE)
                label_font = ImageFont.truetype(font_path, LABEL_FONT_SIZE)
                break
            except:
                continue

    if not title_font:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    # Add card number badge (top right)
    badge_text = f"{card_index + 1}/{total_cards}"
    try:
        bbox = draw.textbbox((0, 0), badge_text, font=label_font)
        badge_width = bbox[2] - bbox[0] + 30
        badge_height = bbox[3] - bbox[1] + 20
    except:
        badge_width = len(badge_text) * 15 + 30
        badge_height = 40

    badge_x = CARD_SIZE - PADDING - badge_width
    badge_y = PADDING - 10

    # Badge background
    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)],
        radius=20,
        fill=scheme['accent']
    )

    # Badge text
    text_x = badge_x + 15
    text_y = badge_y + 10
    draw.text((text_x, text_y), badge_text, fill=(255, 255, 255), font=label_font)

    # Start content
    y_position = PADDING + 80

    # Draw title with proper line wrapping
    content_width = CARD_SIZE - (2 * PADDING)
    title_lines = wrap_text(card['title'], title_font, content_width, draw)

    for line in title_lines[:2]:  # Max 2 lines for title
        draw.text(
            (PADDING, y_position),
            line,
            fill=scheme['title'],
            font=title_font
        )
        y_position += int(TITLE_FONT_SIZE * 1.2)

    # Decorative underline
    y_position += 20
    draw.rectangle(
        [(PADDING, y_position), (PADDING + 80, y_position + 5)],
        fill=scheme['accent']
    )

    y_position += 45

    # Draw content
    paragraphs = card['content'].split('\n\n')
    max_y = CARD_SIZE - PADDING - 120

    for para_idx, para in enumerate(paragraphs):
        if y_position >= max_y:
            break

        # Handle bullet points
        if para.strip().startswith('•'):
            # Draw bullet
            bullet_size = 8
            bullet_x = PADDING + 5
            bullet_y = y_position + 12
            draw.ellipse(
                [(bullet_x, bullet_y), (bullet_x + bullet_size, bullet_y + bullet_size)],
                fill=scheme['accent']
            )
            content_x = PADDING + 28
            para_content = para.strip()[1:].strip()
        else:
            content_x = PADDING
            para_content = para

        # Wrap and draw text
        body_lines = wrap_text(para_content, body_font, content_width - 28, draw)

        for line in body_lines:
            if y_position >= max_y:
                break

            draw.text(
                (content_x, y_position),
                line,
                fill=scheme['body'],
                font=body_font
            )
            y_position += int(BODY_FONT_SIZE * LINE_SPACING)

        y_position += 20  # Space between paragraphs

    # Bottom section
    bottom_y = CARD_SIZE - PADDING - 35

    # Subtle divider line
    draw.line(
        [(PADDING, bottom_y - 10), (CARD_SIZE - PADDING, bottom_y - 10)],
        fill=scheme['accent'],
        width=2
    )

    # Watermark
    draw.text(
        (PADDING, bottom_y + 5),
        WATERMARK_TEXT,
        fill=(150, 150, 150),
        font=label_font
    )

    # Small decorative accent (bottom right)
    accent_x = CARD_SIZE - PADDING - 15
    accent_y = bottom_y
    draw.rectangle(
        [(accent_x, accent_y), (accent_x + 15, accent_y + 30)],
        fill=scheme['accent']
    )

    # Save
    img.save(output_path, 'JPEG', quality=95)
    print(f"✅ {card_index + 1}/{total_cards} - {scheme['name']}")

def sanitize_filename(text):
    """Clean filename"""
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text[:50]

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <html_file_path> [output_dir]")
        print("\nExample:")
        print("  python generate.py ../blog/2025/llm/index.html")
        sys.exit(1)

    html_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'

    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        sys.exit(1)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"📖 Parsing: {html_file}")
    cards = parse_html(html_file)
    print(f"📊 Found {len(cards)} cards\n")

    if not cards:
        print("❌ No H2/H3 headings found")
        sys.exit(1)

    print(f"🎨 Generating professional cards...")
    print(f"{'─' * 40}")

    for i, card in enumerate(cards):
        filename = f"{i+1}_{sanitize_filename(card['title'])}.jpg"
        output_path = os.path.join(output_dir, filename)
        generate_card_image(card, output_path, i, len(cards))

    print(f"{'─' * 40}")
    print(f"\n✨ Done! {len(cards)} cards → {output_dir}/")
    print(f"📂 open {output_dir}")

if __name__ == '__main__':
    main()
