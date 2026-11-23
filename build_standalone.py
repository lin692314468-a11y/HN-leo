"""Package all browser assets into the optional offline HTML edition."""
import base64
from pathlib import Path
root=Path(__file__).resolve().parent
dist=root/'dist'
html=(dist/'index.html').read_text().replace('?v=languages7', '')
html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+(dist/'style.css').read_text()+'</style>')
for name in ['uploads.js','translation.js','app.js']:
    js=(dist/name).read_text()
    if name=='app.js':
        data='data:image/jpeg;base64,'+base64.b64encode((dist/'reference-top.jpg').read_bytes()).decode()
        js=js.replace("fetch('reference-top.jpg')",'fetch('+repr(data)+')')
    html=html.replace('<script src="'+name+'"></script>','<script>'+js+'</script>')
(root/'HN爆单出品.html').write_text(html)
