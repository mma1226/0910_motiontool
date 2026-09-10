import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
tpl = open(BASE+'build/app.tpl.html').read()
data = open(BASE+'build/tiles.json').read()
body = tpl.replace('__DATA__', data)

art = BASE+'build/artifact.html'
open(art,'w').write(body)

head, rest = body.split('<div class="app">', 1)
local = BASE+'cube-motion.html'
open(local,'w').write(
 '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
 '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
 '<style>html,body{margin:0}[hidden]{display:none!important}</style>\n'
 + head.rstrip() + '\n</head>\n<body>\n<div class="app">' + rest + '\n</body>\n</html>\n')
for f in (art, local): print(f, os.path.getsize(f))
