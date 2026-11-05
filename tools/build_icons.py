# Icônes du site (onglet du navigateur, résultats Google, écran d'accueil du téléphone) à partir du dessin du logo.
# Usage : python tools/build_icons.py chemin/vers/le-dessin.jpg   (image carrée)
import os, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
im = Image.open(sys.argv[1]).convert('RGB')
assert im.width == im.height, 'le dessin doit être carré'
im.save(os.path.join(ROOT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])          # Google veut un multiple de 48 px
im.resize((192, 192), Image.LANCZOS).save(os.path.join(ROOT, 'img', 'icon-192.png'))
im.resize((180, 180), Image.LANCZOS).save(os.path.join(ROOT, 'apple-touch-icon.png'))     # iPhone, écran d'accueil
print('ok')
