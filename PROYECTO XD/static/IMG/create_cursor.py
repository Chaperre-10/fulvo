from PIL import Image

img = Image.open('trionda.jpg')
img = img.convert('RGBA')
img = img.resize((64, 64), Image.LANCZOS)
img.save('trionda_cursor.png')
print('CREATED')
