from PIL import Image
from io import BytesIO
import json, requests

HOST = 'https://www.bungie.net'

man_paths_res = requests.get(HOST + '/Platform/Destiny2/Manifest')
man_paths = json.loads(man_paths_res.content)
path = man_paths['Response']['jsonWorldContentPaths']['en']
man_res = requests.get(HOST + path)
manifest = json.loads(man_res.content)

shaders = {}
for i in manifest['DestinyInventoryItemDefinition'].values():
    try:
        if i['itemTypeDisplayName'] == 'Shader':
            shaders[i['displayProperties']['name']] = i['displayProperties']['icon']
    except:
        continue

for name, url in shaders.items():
    res = requests.get(HOST + url)
    raw_img = BytesIO(res.content)
    with Image.open(raw_img) as img:

        #prepare image
        img = img.crop((26, 26, 70, 70))
        img = img.rotate(45, resample=Image.BICUBIC, expand=True)

        #break image into quadrants
        tl = img.crop((0, 0, 32, 32))
        tr = img.crop((32, 0, 64, 32))
        bl = img.crop((0, 32, 32, 64))
        br = img.crop((32, 32, 64, 64))

        #get the color palettes for each quadrant
        palettes = []
        for quad in [tl, tr, bl, br]:

            quant = quad.quantize(6)
            pal = quant.getpalette()
            clr_codes = pal[:15]

            clrs = []
            for i in range(0, 12, 3):
                clrs.append(clr_codes[i:i + 3])
            palettes.append(clrs)

        #create grid of colored squares
        grid = Image.new('RGB', (128, 128), (0, 0, 0))
        ypos = 0
        for pal in palettes:

            row = Image.new('RGB', (128, 32), (0, 0, 0))
            xpos = 0
            for clr in pal:
                square = Image.new('RGB', (32, 32), tuple(clr))
                row.paste(square, (xpos, 0))
                xpos += 32

            grid.paste(row, (0, ypos))
            ypos += 32

        grid.save(name + ' - Palette.jpg')