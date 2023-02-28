import os, math
from PIL import Image

textures = os.listdir('textures')

print(f'Miniblock Count: {len(textures)}')

width = height = math.ceil(math.sqrt(len(textures)))
print(f'Generating a {width} x {height} mosaic')
gallery = Image.new("RGBA", (width*8, height*8))

scale = 3

x = 0
y = 0
for textureFilename in textures:
  if not textureFilename.endswith('.png'): continue
  miniblock = Image.open(f'textures/{textureFilename}').convert("RGBA")
  preview = Image.alpha_composite(miniblock.crop((0,0,8,8)), miniblock.crop((8*6,0,8*6+8,8)))
  gallery.paste(preview, (x, y))
  x += 8
  if x >= width * 8:
    x = 0
    y += 8

gallery = gallery.resize((width*8*scale, height*8*scale), Image.Resampling.NEAREST)

gallery.save('gallery.png')