#!/usr/bin/env python3
"""
Generate index.html from index.template.html using content from content.md

This script parses content.md, splits by --- separators, and replaces 
placeholders in the template to generate the final HTML file.

Section mapping (top-to-bottom, left-to-right):
- Section 0: Header banner
- Section 1: Gold box
- Section 2: Dark Teal box
- Section 3: Orange box
- Section 4: Teal box
"""

import re
import sys
from pathlib import Path
from html import escape


def parse_section(text):
    """Parse a section to extract title (before ===) and content (after ===)"""
    lines = text.strip().split('\n')
    title_lines = []
    content_lines = []
    found_separator = False
    
    for line in lines:
        # Check if this line is === separator
        if re.match(r'^=+$', line.strip()):
            found_separator = True
            continue
        
        if not found_separator:
            # Before === - part of title
            if line.strip():
                title_lines.append(line.strip())
        else:
            # After === - content
            if line.strip():
                content_lines.append(line.strip())
    
    # If no === found, first line is title, rest is content
    if not found_separator and title_lines:
        content_lines = title_lines[1:]
        title_lines = [title_lines[0]]
    
    return {
        'title': '<br>'.join(title_lines),
        'lines': content_lines
    }


def format_paragraph(text, css_class='box-text', indent=16):
    """Format a paragraph with given CSS class"""
    spaces = ' ' * indent
    escaped = escape(text)
    return f'{spaces}<p class="{css_class}">{escaped}</p>'


def main():
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    content_path = root_dir / 'content.md'
    template_path = root_dir / 'index.template.html'
    output_path = root_dir / 'index.html'
    
    # Verify files exist
    if not content_path.exists():
        print(f'Error: Content file not found: {content_path}', file=sys.stderr)
        sys.exit(1)
    if not template_path.exists():
        print(f'Error: Template file not found: {template_path}', file=sys.stderr)
        sys.exit(1)
    
    # Read and parse content.md
    content = content_path.read_text(encoding='utf-8')
    sections = [s.strip() for s in re.split(r'\n---\n', content) if s.strip()]
    
    print(f'Parsing content.md...')
    print(f'  Found {len(sections)} sections')
    
    # Parse all sections
    parsed = [parse_section(section) for section in sections]
    
    for i, section in enumerate(parsed):
        title_display = section['title'].replace('<br>', ' / ')
        print(f'  Section {i}: {title_display}')
    
    # === Build content for each placeholder ===
    # 5 sections → 5 boxes: Header, Gold, Dark Teal, Orange, Teal
    
    # HEADER BANNER: Section 0
    header_title = parsed[0]['title']  # Already has <br> for line breaks
    header_lines = []
    for line in parsed[0]['lines']:
        if re.match(r'^TL;DR', line):
            header_lines.append(f'                <p class="header-text-line header-bold">{escape(line)}</p>')
        else:
            header_lines.append(f'                <p class="header-text-line">{escape(line)}</p>')
    header_content = '\n'.join(header_lines)
    
    # GOLD BOX: Section 1
    gold_title = escape(parsed[1]['title'])
    gold_lines = [format_paragraph(line) for line in parsed[1]['lines']]
    gold_content = '\n'.join(gold_lines)
    
    # DARK TEAL BOX: Section 2
    dark_teal_title = parsed[2]['title']
    dark_teal_lines = [format_paragraph(line, 'box-text box-text-small') for line in parsed[2]['lines']]
    dark_teal_content = '\n'.join(dark_teal_lines)
    
    # ORANGE BOX: Section 3
    orange_title = escape(parsed[3]['title'])
    # Main text (all lines except last) + emoji
    main_text = ' '.join(parsed[3]['lines'][:-1]) + ' 🤎'
    orange_lines = [format_paragraph(main_text)]
    # Cost line (last line)
    orange_lines.append(format_paragraph(parsed[3]['lines'][-1], 'box-text box-text-bold'))
    orange_content = '\n'.join(orange_lines)
    
    # TEAL BOX: Section 4
    teal_title = escape(parsed[4]['title'])
    teal_lines = []
    # Process bullet points - combine continuation lines
    current_fact = ''
    for line in parsed[4]['lines']:
        if line.startswith('-'):
            # New bullet point - save previous if exists
            if current_fact:
                teal_lines.append(format_paragraph(current_fact, 'box-text box-text-small'))
            current_fact = line
        else:
            # Continuation of previous bullet
            current_fact += ' ' + line
    # Don't forget last bullet
    if current_fact:
        teal_lines.append(format_paragraph(current_fact, 'box-text box-text-small'))
    teal_content = '\n'.join(teal_lines)
    
    # === Generate HTML from template ===
    print('\nGenerating index.html from template...')
    
    template = template_path.read_text(encoding='utf-8')
    
    html = template \
        .replace('{{HEADER_TITLE}}', header_title) \
        .replace('{{HEADER_CONTENT}}', header_content) \
        .replace('{{GOLD_TITLE}}', gold_title) \
        .replace('{{GOLD_CONTENT}}', gold_content) \
        .replace('{{DARK_TEAL_TITLE}}', dark_teal_title) \
        .replace('{{DARK_TEAL_CONTENT}}', dark_teal_content) \
        .replace('{{ORANGE_TITLE}}', orange_title) \
        .replace('{{ORANGE_CONTENT}}', orange_content) \
        .replace('{{TEAL_TITLE}}', teal_title) \
        .replace('{{TEAL_CONTENT}}', teal_content)
    
    # Write output
    output_path.write_text(html, encoding='utf-8')
    
    print('Done! Generated index.html')
    print('\nContent mapping (5 sections -> 5 boxes):')
    print(f'  Header:     Section 0 - {parsed[0]["title"].replace("<br>", " / ")}')
    print(f'  Gold:       Section 1 - {parsed[1]["title"]}')
    print(f'  Dark Teal:  Section 2 - {parsed[2]["title"]}')
    print(f'  Orange:     Section 3 - {parsed[3]["title"]}')
    print(f'  Teal:       Section 4 - {parsed[4]["title"]}')


if __name__ == '__main__':
    main()
