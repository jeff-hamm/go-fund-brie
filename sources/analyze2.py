import re

c = open(r'C:\Users\Jumper\Projects\gofundbrie\Zelda Fundraising Flyer.svg', 'r', encoding='utf-8').read()
idx = c.index('</defs>') + 7
b = c[idx:]

# Find all groups with transforms
groups = list(re.finditer(r'<g\s+transform="matrix\(([^)]+)\)"[^>]*>', b))
print(f'Found {len(groups)} top-level groups')

for i, g in enumerate(groups):
    t = g.group(1)
    # Find the matching close tag - simple approach: get next ~2000 chars
    start = g.start()
    snippet = b[start:start+3000]
    
    # Count rect, path, text, image, tspan elements
    rects = re.findall(r'<rect\s+([^>]+)', snippet)
    paths = re.findall(r'<path\s+([^>]+)', snippet)
    texts = re.findall(r'<text\s+([^>]*)', snippet)
    tspans = re.findall(r'<tspan\s+([^>]*)', snippet)
    images = re.findall(r'<image\s+([^>]+)', snippet)
    clips = re.findall(r'clip-path="url\(#([^)]+)\)"', snippet)
    
    print(f'\n--- Group {i}: transform({t}) ---')
    for r in rects:
        w = re.search(r'width="([^"]+)"', r)
        h = re.search(r'height="([^"]+)"', r)
        fill = re.search(r'style="fill:([^;"]+)', r)
        x = re.search(r' x="([^"]+)"', r)
        y = re.search(r' y="([^"]+)"', r)
        rx = re.search(r'rx="([^"]+)"', r)
        print(f'  RECT: {w.group(1) if w else "?"}x{h.group(1) if h else "?"} '
              f'at ({x.group(1) if x else "0"},{y.group(1) if y else "0"}) '
              f'fill={fill.group(1) if fill else "?"} '
              f'rx={rx.group(1) if rx else "0"}')
    for p in paths[:3]:
        fill = re.search(r'style="fill:([^;"]+)', p)
        d = re.search(r'd="([^"]{0,80})', p)
        print(f'  PATH: fill={fill.group(1) if fill else "?"} d={d.group(1) if d else "?"}...')
    if len(paths) > 3:
        print(f'  ... and {len(paths)-3} more paths')
    for t2 in texts:
        print(f'  TEXT: {t2[:100]}')
    for ts in tspans:
        x = re.search(r'x="([^"]+)"', ts)
        y = re.search(r'y="([^"]+)"', ts)
        fs = re.search(r'font-size:([^;p]+)', ts)
        fw = re.search(r'font-weight:([^;"]+)', ts)
        # Get text content
        ts_match = re.search(r'<tspan[^>]*>([^<]*)</tspan>', snippet[snippet.index(ts[:30]):snippet.index(ts[:30])+200])
        txt = ts_match.group(1) if ts_match else '?'
        print(f'  TSPAN: ({x.group(1) if x else "?"},{y.group(1) if y else "?"}) '
              f'size={fs.group(1) if fs else "?"} weight={fw.group(1) if fw else "?"} '
              f'"{txt[:50]}"')
    for im in images:
        w = re.search(r'width="([^"]+)"', im)
        h = re.search(r'height="([^"]+)"', im)
        clip = re.search(r'clip-path="url\(#([^)]+)\)"', im)
        print(f'  IMAGE: {w.group(1) if w else "?"}x{h.group(1) if h else "?"} clip={clip.group(1) if clip else "none"}')
