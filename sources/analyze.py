import re

c = open(r'C:\Users\Jumper\Projects\gofundbrie\Zelda Fundraising Flyer.svg', 'r', encoding='utf-8').read()
idx = c.index('</defs>') + 7
b = c[idx:]
ts = list(re.finditer(r'transform="matrix\(([^)]+)\)"', b))
print(f'Found {len(ts)} transforms')
for i, m in enumerate(ts):
    t = m.group(1)
    after = b[m.start():m.start()+500]
    fills = re.findall(r'fill="#([a-f0-9]+)"', after)
    has_img = 'IMG' if '<image' in after else '---'
    fill = fills[0] if fills else 'none'
    print(f'{i}: t({t}) fill=#{fill} {has_img}')
