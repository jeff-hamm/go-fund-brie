import re

c = open(r'C:\Users\Jumper\Projects\gofundbrie\Zelda Fundraising Flyer.svg', 'r', encoding='utf-8').read()
idx = c.index('</defs>') + 7
b = c[idx:]

# Get ALL image elements with width AND height
images = list(re.finditer(r'<image\s+([^>]+)>', b))
print(f'Found {len(images)} images')
for i, im in enumerate(images):
    attrs = im.group(1)
    w = re.search(r'width="([^"]+)"', attrs)
    h = re.search(r'height="([^"]+)"', attrs)
    clip = re.search(r'clip-path="url\(#([^)]+)\)"', attrs)
    # Find parent transform
    before = b[:im.start()]
    last_t = list(re.finditer(r'transform="matrix\(([^)]+)\)"', before))
    parent_t = last_t[-1].group(1) if last_t else 'none'
    print(f'  Image {i}: {w.group(1) if w else "?"}x{h.group(1) if h else "?"} clip={clip.group(1) if clip else "none"} parent_t=({parent_t})')

# Get clip-path definitions
print('\n--- Clip paths ---')
clips = list(re.finditer(r'<clipPath id="([^"]+)"[^>]*>\s*<(rect|path|circle)\s+([^>]+)>', c))
for cl in clips:
    cid = cl.group(1)
    el = cl.group(2)
    attrs = cl.group(3)
    # Extract useful attributes
    if el == 'rect':
        x = re.search(r'x="([^"]+)"', attrs)
        y = re.search(r'y="([^"]+)"', attrs)
        w = re.search(r'width="([^"]+)"', attrs)
        h = re.search(r'height="([^"]+)"', attrs)
        rx = re.search(r'rx="([^"]+)"', attrs)
        print(f'  {cid}: RECT ({x.group(1) if x else "0"},{y.group(1) if y else "0"}) '
              f'{w.group(1) if w else "?"}x{h.group(1) if h else "?"} rx={rx.group(1) if rx else "0"}')
    else:
        print(f'  {cid}: {el} {attrs[:80]}...')

# Look specifically at what's INSIDE the dark teal box area
# (373,232) to (373+209, 232+261) = (373, 232) to (582, 493)
print('\n--- Elements in dark teal region (373-582, 232-493) ---')
# Group 6 and 7 are the photo. Let me check if there's anything else
# Look at all group 15 content more carefully (the one at 72, 644)
print('\n--- Group 15 detail (72, 644 - orange box Venmo area) ---')
g15_start = b.index('transform="matrix(1, 0, 0, 1, 72, 644)"')
g15_content = b[g15_start:g15_start+2000]
# Find the first large path - this is the rounded rect
first_path = re.search(r'<path[^>]+d="([^"]{0,200})"', g15_content)
if first_path:
    print(f'  First path d: {first_path.group(1)[:150]}...')

# Check path fills in group 15
fills15 = re.findall(r'style="fill:([^;"]+)', g15_content)
print(f'  Fills in group 15: {fills15}')

# Check rendering order of entire dark teal box area
print('\n--- Groups nesting (first 6) ---')
for i in range(min(6, len(images))):
    im = images[i]
    before = b[:im.start()]
    # Count open/close g tags
    opens = len(re.findall(r'<g\s', before))
    closes = len(re.findall(r'</g>', before))
    print(f'  Image {i}: nesting depth = {opens - closes}')
