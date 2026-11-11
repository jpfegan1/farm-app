# Per-variety Wikimedia Commons photos for peach & nectarine cultivars.
# A file is accepted only if its TITLE names the variety AND names the fruit (peach/nectarine/Prunus persica/…),
# and its licence is CC BY*/CC0/PD. Saved as crops/img/var_<crop>_<slug>.webp (160px), credits in var_photo_credits.json.
import json,urllib.request,urllib.parse,time,re,io,os,sys,unicodedata
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__))
from fetch_photos import UA, strip
import stone_fruit as SF
OUT=os.path.join(os.path.dirname(__file__),'..','crops','img')
CRED=os.path.join(os.path.dirname(__file__),'var_photo_credits.json')
cred=json.load(open(CRED)) if os.path.exists(CRED) else {}
REJ=json.load(open(os.path.join(os.path.dirname(__file__),'var_photo_rejects.json')))['rejected'] if os.path.exists(os.path.join(os.path.dirname(__file__),'var_photo_rejects.json')) else []  # manually reviewed false matches
LIC=re.compile(r'^(CC BY|CC-BY|CC0|Public domain|PD)',re.I)
BAD=re.compile(r'map\b|distribution|herbar|diagram|chart|logo|stamp|\.svg|packet|label|sign\b|coin|banknote|aphid|insect|disease|curl|blight|damage|recipe|cake|pie\b|jam\b|cocktail|logo|seedling|leaf curl|\bsoap\b|perfume|shop|market stall|cultivar list',re.I)
ART=re.compile(r'watercolou?r|painting|pomolog|illustrat|plate|drawing|lithograph|chromolith|engraving|tafel|\bfig\.',re.I)
FRUIT=re.compile(r'peach|nectarin|persica|pfirsich|p[eê]che|brugnon|melocoton|perzik|pesca|pesco|nektarin|durazno',re.I)
def slug(s): return re.sub(r'[^a-z0-9]+','_',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('_')
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def keyname(n):
    n=re.sub(r'\s*\((peach|q-1-8)\)','',n,flags=re.I)
    return n.replace("’","'")
def api(p):
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({**p,'format':'json'})
    for t in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except Exception: time.sleep(3)
    return {}
def candidates(q):
    d=api({'action':'query','generator':'search','gsrnamespace':6,'gsrsearch':q,'gsrlimit':30,'prop':'imageinfo','iiprop':'url|extmetadata|size|mime','iiurlwidth':400})
    out=[]
    for p in sorted(d.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',99)):
        t=p['title']; ii=(p.get('imageinfo') or [{}])[0]; md=ii.get('extmetadata',{})
        if ii.get('mime') not in ('image/jpeg','image/png','image/webp'): continue
        lic=strip(md.get('LicenseShortName',{}).get('value',''))
        if BAD.search(t) or not LIC.match(lic): continue
        if ii.get('width',0)<300 or ii.get('height',0)<250: continue
        out.append(dict(file=t,url=ii.get('thumburl'),page=ii.get('descriptionurl'),author=strip(md.get('Artist',{}).get('value',''))[:120] or 'Unknown',licence=lic,kind='illustration' if ART.search(t) else 'photo'))
    return out
def title_ok(title,name,crop):
    t=title[5:].rsplit('.',1)[0].replace("’","'").replace("‘","'")
    if re.search(r'still.?life|stilleben|nature morte|basket|bowl|table',t,re.I): return False
    nm=re.escape(name.lower()).replace("\\ ",r"[\s_\-]*").replace("'",".?")
    fr=r'(peach(es)?|nectarines?|prunus persica|persica|pfirsich|p[eê]che|brugnon|nektarine?|perzik|pesca|durazno)'
    sep=r"[^a-z0-9]{0,6}(?:(?:cultivar|cv|var|variety|sorte|vari[eé]t[eé])[^a-z0-9]{0,4})?"
    tl=t.lower()
    if not (re.search(r'(?<![a-z])'+nm+sep+fr,tl) or re.search(fr+sep+nm+r'(?![a-z])',tl)): return False
    if crop=='peach' and re.search(r'nectarin|nektarin|brugnon',t,re.I) and not re.search(r'peach|pfirsich',t,re.I): return False
    if crop=='nectarine' and not re.search(r'nectarin|nektarin|brugnon|nucipersica',t,re.I): return False
    return True
ONLY=set(sys.argv[1:])
for crop,L in (('peach',SF.PEACH),('nectarine',SF.NECT)):
    for v in L:
        key=f'{crop}/{v["name"]}'
        if ONLY and v['name'] not in ONLY: continue
        if key in cred and not ONLY: continue
        name=keyname(v['name']); fw='nectarine' if crop=='nectarine' else 'peach'
        qs=[f'intitle:"{name}" {fw}', f'"{name}" Prunus persica', f'intitle:"{name}" persica', f'"{name}" {fw}']
        got=None; seen=set()
        for q in qs:
            cs=candidates(q); time.sleep(0.4)
            cs=[c for c in cs if c['file'] not in seen and title_ok(c['file'],name,crop) and not any(c['file'].startswith(r) for r in REJ)]
            cs.sort(key=lambda c:(c['kind']!='photo',))
            for c in cs[:5]:
                seen.add(c['file'])
                try: im=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(c['url'],headers=UA),timeout=30).read())).convert('RGB')
                except Exception: continue
                got=(c,im); break
            if got: break
        if not got: cred[key]=None; print('NONE',key,flush=True)
        else:
            c,im=got; w,h=im.size; s=min(w,h)
            im=im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)).resize((160,160),Image.LANCZOS)
            fn=f'var_{crop}_{slug(v["name"])}.webp'; im.save(os.path.join(OUT,fn),'WEBP',quality=72,method=6)
            c['img']='img/'+fn; cred[key]=c; print('OK',key,'|',c['file'][:90],'|',c['licence'],c['kind'],flush=True)
        json.dump(cred,open(CRED,'w'),indent=0,ensure_ascii=False)
