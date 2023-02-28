import sys
from PIL import Image

# tilts miniblock 90 degrees back

path = sys.argv[1]

block = Image.open(path)
rotated = Image.new('RGBA', (96, 8))

# 0 1 2 3 4 5
# F B L R U D

# F -> U
rotated.paste(block.crop((0,0,8,8)), (4*8,0))
# U -> B
rotated.paste(block.crop((4*8,0,4*8+8,8)).transpose(Image.FLIP_TOP_BOTTOM), (1*8,0))
# B -> D
rotated.paste(block.crop((1*8,0,1*8+8,8)), (5*8,0))
# D -> F
rotated.paste(block.crop((5*8,0,5*8+8,8)).transpose(Image.FLIP_TOP_BOTTOM), (0,0))
# R 90cw
rotated.paste(block.crop((3*8,0,3*8+8,8)).rotate(-90), (3*8,0))
# L 90ccw
rotated.paste(block.crop((2*8,0,2*8+8,8)).rotate(90), (2*8,0))


## Outer Layer

# F -> U
rotated.paste(block.crop((0+48,0,8+48,8)), (4*8+48,0))
# U -> B
rotated.paste(block.crop((4*8+48,0,4*8+8+48,8)).transpose(Image.FLIP_TOP_BOTTOM), (1*8+48,0))
# B -> D
rotated.paste(block.crop((1*8+48,0,1*8+8+48,8)), (5*8+48,0))
# D -> F
rotated.paste(block.crop((5*8+48,0,5*8+8+48,8)).transpose(Image.FLIP_TOP_BOTTOM), (0+48,0))
# R 90cw
rotated.paste(block.crop((3*8+48,0,3*8+8+48,8)).rotate(-90), (3*8+48,0))
# L 90ccw
rotated.paste(block.crop((2*8+48,0,2*8+8+48,8)).rotate(90), (2*8+48,0))

rotated.save(f'{path.removesuffix(".png")}_rotated.png')