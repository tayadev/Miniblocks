from beet import Context, Function, LootTable
import json, base64, os, time
from PIL import Image
from mojang import Client
from dotenv import load_dotenv
load_dotenv()

data = {}
with open('data.json') as f:
  data = json.load(f)

def miniblock_nbt(name, textureId):
  return 'display:{Name:\'[{"text":"Mini ","italic":false,"color":"white"},{"text":"' + name + '"}]\'},SkullOwner:{Id:[I;0,0,0,0],Name:"' + name + '",Properties:{textures:[{Value:"' + str(base64.b64encode(('{"textures":{"SKIN":{"url":"http://textures.minecraft.net/texture/' + textureId + '"}}}').encode('utf-8')), 'utf-8') + '"}]}}'

mcSkinCoords = {
  "front": (8, 8),
  "back": (24, 8),
  "left": (16, 8),
  "right": (0, 8),
  "top": (8, 0),
  "bottom": (16, 0),
  "front_outer": (40, 8),
  "back_outer": (56, 8),
  "left_outer": (48, 8),
  "right_outer": (32, 8),
  "top_outer": (40, 0),
  "bottom_outer": (48, 0),
}

customSkinCoords = {
  "front": (0, 0),
  "back": (8, 0),
  "left": (16, 0),
  "right": (24, 0),
  "top": (32, 0),
  "bottom": (40, 0),
  "front_outer": (48, 0),
  "back_outer": (56, 0),
  "left_outer": (64, 0),
  "right_outer": (72, 0),
  "top_outer": (80, 0),
  "bottom_outer": (88, 0),
}

def mcSkinToCustom(skin):
  customTex = Image.new(mode="RGBA", size=(96, 8))
  for key, coords in mcSkinCoords.items():
    customTex.paste(skin.crop((coords[0],coords[1],coords[0]+8,coords[1]+8)), customSkinCoords[key])
  return customTex

def customToMcSkin(image):
  skin = Image.new(mode="RGBA", size=(64, 64))
  for key, coords in customSkinCoords.items():
    skin.paste(image.crop((coords[0],coords[1],coords[0]+8,coords[1]+8)), mcSkinCoords[key])
  return skin

def setSkin(client, path = None, url = None, variant = "classic"):
  waitTime = 10
  while True:
    try:
      client.change_skin(variant=variant, image_path=path, url=url)
      profile = client.get_profile()
      break
    except:
      print(f'Failed skin upload, retrying in {waitTime} seconds')
      time.sleep(waitTime)
      waitTime += 10
  return profile.skins[0].url.rsplit('/',1)[-1]

def uploadTextures(filenames):
  print('Logging in to Mojang')
  client = Client(os.getenv("EMAIL"), os.getenv("PASSWORD"))
  profile = client.get_profile()
  print(f'Logged in as {profile.name}')

  print('Creating skin backup point')
  skin_backup = profile.skins[0]

  for i, filename in enumerate(filenames):
    print(f'Uploading {i+1}/{len(filenames)} - {filename}')
    skin = customToMcSkin(Image.open(filename))
    skin.save('temp.png')
    texId = setSkin(client, path = 'temp.png')
    print('Generated url:', f'http://textures.minecraft.net/texture/{texId}')
    data[filename.rsplit('/', 1)[-1].removesuffix('.png')] = texId
    with open('data.json', 'w') as outfile:
      json.dump(data, outfile, indent=2, sort_keys=True)
    time.sleep(4)
    os.remove('temp.png')
  
  print('Restoring skin')
  setSkin(client, url = skin_backup.url, variant = skin_backup.variant)

def beet_default(ctx: Context):
  print("Generating Miniblocks")

  toUpload = []
  for textureFilename in os.listdir('textures'):
    if not textureFilename.endswith('.png'): continue
    name = textureFilename.removesuffix('.png')
    if name in data.keys(): continue
    print(f'Found unregistered texture "{textureFilename}"')
    texture = Image.open(f'textures/{textureFilename}')
    if texture.size in [(64, 64), (64, 32)]:
      print('-> Texture is in default skin format, transforming to custom one')
      mcSkinToCustom(texture).save(f'textures/{textureFilename}')
    toUpload.append(f'textures/{textureFilename}')
  if len(toUpload) > 0:
    if os.getenv('EMAIL') and os.getenv('PASSWORD'):
      uploadTextures(toUpload)
    else:
      print("SKIPPING texture upload, because no login details were provided")

  print("Generating Functions and LootTables")
  for identifier, textureId in data.items():
    ctx.data[f'miniblocks:give/{identifier}'] = Function(f'give @s player_head{{{miniblock_nbt(identifier, textureId)}}}')
    ctx.data[f'miniblocks:{identifier}'] = LootTable({
      "pools": [
        {
          "rolls": 1,
          "entries": [
            {
              "type": "minecraft:item",
              "name": "minecraft:player_head",
              "functions": [
                {
                  "function": "minecraft:set_nbt",
                  "tag": f'{{{miniblock_nbt(identifier, textureId)}}}'
                }
              ]
            }
          ]
        }
      ]
    })
  
  print(f'Generated {len(data)} Miniblocks')