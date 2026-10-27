"""Prepara foto e testi del portfolio e scrive foto.js.

1. Ogni foto caricata in foto/ (jpg, png, tif, webp...) viene convertita in WebP,
   lato lungo massimo 2400 px, senza ritagli; l'originale viene sostituito.
2. Per ogni progetto crea la miniatura in miniature/ dalla prima foto.
3. Legge testo.txt di ogni progetto (titolo, scheda, categoria, tag, testo).
4. Scrive foto.js con foto e testi di ogni progetto, nell'ordine delle cartelle.
"""
import base64, hashlib, html, json, os, re, shutil, subprocess, sys
from PIL import Image, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FOTO, MINI = 'foto', 'miniature'
MAX_SIDE, THUMB_W = 3000, 800
EXT = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp', '.bmp', '.gif'}
VID = {'.mp4', '.webm'}            # video pronti per il web
VID_RAW = {'.mov', '.m4v', '.avi'}  # convertiti in .mp4 se ffmpeg è disponibile
SEC = {'00_home': 'home', '01_studio': 'studio', '02_urban': 'urban', '03_interior': 'interior', '04_art': 'art'}
os.chdir(ROOT)

natkey = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def rgb(im):
    im = ImageOps.exif_transpose(im)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        return im.convert('RGBA')
    return im.convert('RGB')

def fit(im, side):
    w, h = im.size
    s = side / max(w, h)
    return im.resize((round(w * s), round(h * s)), Image.LANCZOS) if s < 1 else im

# 1. conversione
for dp, _, files in os.walk(FOTO):
    for f in sorted(files):
        stem, ext = os.path.splitext(f)
        ext = ext.lower()
        if ext not in EXT:
            continue
        src = os.path.join(dp, f)
        dst = os.path.join(dp, stem + '.webp')
        with Image.open(src) as im0:
            big = max(im0.size) > MAX_SIDE
            if ext == '.webp' and not big:
                continue
            im = fit(rgb(im0), MAX_SIDE)
        im.save(dst + '.tmp', 'WEBP', quality=90, method=6)
        os.replace(dst + '.tmp', dst)
        if src != dst:
            os.remove(src)
        print('foto pronta:', dst)

# 1b. video: .mov -> .mp4 (H.264, 1080p) e immagine di anteprima <nome>.poster.webp
FF = shutil.which('ffmpeg')
for dp, _, files in os.walk(FOTO):
    for f in sorted(files):
        stem, ext = os.path.splitext(f)
        ext = ext.lower()
        src = os.path.join(dp, f)
        if ext in VID_RAW and FF:
            dst = os.path.join(dp, stem + '.mp4')
            subprocess.run([FF, '-v', 'error', '-y', '-i', src, '-map', '0:v:0', '-map', '0:a:0?',
                            '-vf', "scale='min(1920,iw)':-2", '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                            '-maxrate', '3.5M', '-bufsize', '7M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                            '-movflags', '+faststart', dst + '.tmp.mp4'], check=True)
            os.replace(dst + '.tmp.mp4', dst)
            os.remove(src)
            print('video pronto:', dst)
            ext, src = '.mp4', dst
        if ext in VID and FF:
            poster = os.path.join(dp, stem + '.poster.webp')
            if not os.path.exists(poster):
                subprocess.run([FF, '-v', 'error', '-y', '-ss', '2', '-i', src, '-frames:v', '1',
                                '-c:v', 'libwebp', '-quality', '88', poster], check=True)
                print('anteprima video:', poster)

def photos(folder):
    return sorted([f for f in os.listdir(folder) if f.lower().endswith('.webp') and not f.lower().endswith('.poster.webp')], key=natkey)

def media(folder):
    """Foto e video del progetto, in ordine di nome. Un video è {'v': url, 'p': anteprima}."""
    out = []
    for f in sorted(os.listdir(folder), key=natkey):
        fl = f.lower()
        if fl.endswith('.poster.webp'):
            continue
        if fl.endswith('.webp'):
            out.append(url(os.path.join(folder, f)))
        elif os.path.splitext(fl)[1] in VID:
            stem = os.path.splitext(f)[0]
            poster = os.path.join(folder, stem + '.poster.webp')
            out.append({'v': url(os.path.join(folder, f)), 'p': url(poster) if os.path.exists(poster) else ''})
    return out

def url(path):
    h = hashlib.md5(open(path, 'rb').read()).hexdigest()[:8]
    return f'{path}?v={h}'


def read_text(folder, fallback):
    """testo.txt: righe 'Chiave: valore' in alto, una riga vuota, poi i paragrafi."""
    path = os.path.join(folder, 'testo.txt')
    x = {'title': fallback, 'place': '', 'sub': '', 'tags': [], 'meta': [], 'body': ''}
    if not os.path.exists(path):
        return x
    raw = open(path, encoding='utf-8-sig').read().replace('\r\n', '\n').replace('\r', '\n')
    head, _, body = raw.strip('\n').partition('\n\n')
    for line in head.split('\n'):
        k, sep, v = line.partition(':')
        if not sep:
            continue
        k, v = k.strip(), v.strip()
        kl = k.lower()
        if kl in ('title', 'titolo', 'título'):
            x['title'] = v or fallback
        elif kl in ('place', 'luogo', 'lugar'):
            x['place'] = v
        elif kl in ('category', 'categoria', 'categoría'):
            x['sub'] = v
        elif kl == 'tags':
            x['tags'] = [t.strip() for t in v.split(',') if t.strip()]
        elif kl in ('visible', 'visibile'):
            x['_visible'] = v.lower() not in ('no', 'false', '0', 'off')
        elif kl == 'pin':
            x['_pin'] = v.lower() in ('yes', 'si', 'sì', 'true', '1', 'on')
        elif v:
            x['meta'].append([k, v])
    paras = [re.sub(r'\s*\n\s*', ' ', p).strip() for p in re.split(r'\n\s*\n', body.strip())]
    def fmt(p):
        p = html.escape(p, quote=False)
        return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', p)
    x['body'] = ''.join(f'<p>{fmt(p)}</p>' for p in paras if p)
    return x

PIN = os.environ.get('PORTFOLIO_PIN', '').strip()

def lock(entity, payload):
    """Cifra i dati del progetto con il PIN (PBKDF2 + AES-GCM), decifrabili dal browser solo con il PIN giusto."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    raw = json.dumps(payload, ensure_ascii=False).encode()
    salt = hashlib.sha256(b'er-salt|portfolio').digest()[:16]
    iv = hashlib.sha256(b'er-iv|' + raw + PIN.encode()).digest()[:12]
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=250000).derive(PIN.encode())
    b64 = lambda b: base64.b64encode(b).decode()
    return {'s': b64(salt), 'i': b64(iv), 'd': b64(AESGCM(key).encrypt(iv, raw, None))}

written = set()
data = {'home': [], 'p': {}, 's': {}, 'sec': {}}
for secdir in sorted(os.listdir(FOTO), key=natkey):
    sec = SEC.get(secdir)
    base = os.path.join(FOTO, secdir)
    if not sec or not os.path.isdir(base):
        continue
    if sec == 'home':
        data['home'] = [url(os.path.join(base, f)) for f in photos(base)]
        continue
    for pdir in sorted(os.listdir(base), key=natkey):
        folder = os.path.join(base, pdir)
        if not os.path.isdir(folder):
            continue
        entity = sec + '/' + re.sub(r'^\d+[_-]', '', pdir)
        if sec == 'studio':
            lst = [url(os.path.join(folder, f)) for f in photos(folder)]
            data['s'][entity] = lst
            continue
        lst = media(folder)
        title_guess = re.sub(r'^\d+[_-]', '', pdir).replace('-', ' ').title()
        x = read_text(folder, title_guess)
        visible, locked = x.pop('_visible', True), x.pop('_pin', False)
        if not visible:
            print('nascosto:', entity)
            continue
        if locked and not PIN:
            print('ATTENZIONE: PIN richiesto ma il segreto PORTFOLIO_PIN non c\'è: progetto nascosto:', entity)
            continue
        entry = {'f': lst, 'x': x}
        data['sec'].setdefault(sec, []).append(entity)
        if photos(folder):  # 2. miniatura
            first = os.path.join(folder, photos(folder)[0])
            tdir = os.path.join(MINI, secdir)
            os.makedirs(tdir, exist_ok=True)
            tpath = os.path.join(tdir, pdir + '.webp')
            with Image.open(first) as im:
                im = rgb(im)
                w, h = im.size
                if w > THUMB_W:
                    im = im.resize((THUMB_W, round(h * THUMB_W / w)), Image.LANCZOS)
                im.save(tpath, 'WEBP', quality=85, method=6)
                written.add(tpath)
                if locked:
                    from PIL import ImageFilter
                    bpath = os.path.join(tdir, pdir + '__locked.webp')
                    small = im.resize((max(1, im.width // 8), max(1, im.height // 8)), Image.LANCZOS)
                    small.resize(im.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(14)).save(bpath, 'WEBP', quality=70)
                    written.add(bpath)
            entry['t'] = url(tpath)
        if locked:
            entry = {'f': [], 'x': {'title': x['title'], 'sub': x['sub'], 'tags': [], 'meta': [], 'place': '', 'body': ''},
                     'lock': lock(entity, entry)}
            if photos(folder):
                entry['t'] = url(os.path.join(MINI, secdir, pdir + '__locked.webp'))
            print('protetto con PIN:', entity)
        data['p'][entity] = entry

# miniature di progetti che non esistono più
if os.path.isdir(MINI):
    for dp, _, files in os.walk(MINI):
        for f in files:
            p = os.path.join(dp, f)
            if p not in written:
                os.remove(p)

# 3. elenco per il sito
with open('foto.js', 'w') as fh:
    fh.write('// Generato automaticamente da .github/scripts/build_foto.py: non modificare a mano.\n')
    fh.write('window.ERFOTO = ' + json.dumps(data, ensure_ascii=False, indent=0) + ';\n')
print('foto.js aggiornato:', len(data['p']), 'progetti')
