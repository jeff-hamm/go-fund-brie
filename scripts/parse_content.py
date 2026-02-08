import re
from pathlib import Path

# Read the markdown content
content_path = Path(r'C:\Users\Jumper\Projects\gofundbrie\content.md')
content = content_path.read_text(encoding='utf-8')

# Split by --- separators
sections = [s.strip() for s in content.split('---')]

print(f"Found {len(sections)} sections:")
print("=" * 60)

for i, section in enumerate(sections):
    print(f"\n--- Section {i} ---")
    # Get first 2 lines as preview
    lines = section.split('\n')
    preview = '\n'.join(lines[:3])
    print(preview)
    print(f"... ({len(lines)} total lines)")

# Parse each section to extract title and content
def parse_section(text):
    lines = text.strip().split('\n')
    
    # Find title (lines with === underneath or starting with certain patterns)
    title = None
    content_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if next line is ===
        if i + 1 < len(lines) and lines[i + 1].strip().startswith('==='):
            title = line.strip()
            i += 2  # Skip the === line
            continue
        
        # Regular content line
        if line.strip():
            content_lines.append(line)
        elif content_lines:  # Preserve blank lines within content
            content_lines.append('')
        
        i += 1
    
    # Clean up content
    content_text = '\n'.join(content_lines).strip()
    
    return title, content_text

# Parse all sections
parsed = []
for i, section in enumerate(sections):
    if section.strip():
        title, content = parse_section(section)
        parsed.append({
            'index': i,
            'title': title,
            'content': content,
            'raw': section
        })

print("\n" + "=" * 60)
print("PARSED SECTIONS:")
print("=" * 60)

for p in parsed:
    print(f"\nSection {p['index']}:")
    print(f"  Title: {p['title']}")
    print(f"  Content preview: {p['content'][:100]}...")

# Map sections to boxes (top-to-bottom, left-to-right)
# Gold box (top-left), Dark-teal (top-right - no text), Orange (bottom-left), Teal (bottom-right)

# Sections that have content:
# 0: Header with TL;DR
# 1: More info on surgery
# 2: Halp section
# 3: GoFundBrie
# 4: Zelda facts

box_mapping = {
    'gold': parsed[0],      # First section (TL;DR)
    'orange': parsed[3],    # GoFundBrie section
    'teal': parsed[4]       # Zelda facts section
}

print("\n" + "=" * 60)
print("BOX MAPPING:")
print("=" * 60)
for box, section in box_mapping.items():
    print(f"{box.upper()}: Section {section['index']} - {section['title']}")

# Generate HTML content for each box
def format_for_html(section):
    lines = section['content'].split('\n')
    html_parts = []
    
    # Add title if present
    if section['title']:
        html_parts.append(f'<h2 class="box-title">{section["title"]}</h2>')
    
    # Process content lines
    current_para = []
    for line in lines:
        line = line.strip()
        if not line:
            if current_para:
                html_parts.append(f'<p class="box-text">{"<br>".join(current_para)}</p>')
                current_para = []
        else:
            # Check if it's a list item
            if line.startswith('-'):
                if current_para:
                    html_parts.append(f'<p class="box-text">{"<br>".join(current_para)}</p>')
                    current_para = []
                html_parts.append(f'<p class="box-text">{line}</p>')
            else:
                current_para.append(line)
    
    if current_para:
        html_parts.append(f'<p class="box-text">{"<br>".join(current_para)}</p>')
    
    return '\n                '.join(html_parts)

print("\n" + "=" * 60)
print("GENERATED HTML:")
print("=" * 60)

for box, section in box_mapping.items():
    print(f"\n{box.upper()} BOX:")
    print(format_for_html(section))
