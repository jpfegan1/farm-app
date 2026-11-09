import json,urllib.request,urllib.parse,time,re,io,os,sys
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__))
from crop_list import CROPS
from fetch_photos import Q, UA, strip
OUT=os.path.join(os.path.dirname(__file__),'..','crops','img')
CRED=os.path.join(os.path.dirname(__file__),'photo_credits.json')
cred={}
ONLY=set(sys.argv[1:])
if ONLY and os.path.exists(CRED): cred=json.load(open(CRED))
FORCE=json.load(open(os.path.join(os.path.dirname(__file__),'photo_overrides.json'))) if os.path.exists(os.path.join(os.path.dirname(__file__),'photo_overrides.json')) else {}
BAD=re.compile(r'map|distribution|herbar|drawing|illustrat|diagram|chart|logo|stamp|\.svg|\.tif|packet|plate|k[öo]hler|thom[ée]|sturm|lindman|flora|botanical|museum|book|label|sign|\bbee|apis|bombus|insect|butterfl|larva|caterpill|beetle|moth\b|aphid|\bfly\b|hoverfl|grasshopper|wasp|spider|bug\b|weevil|snail|slug|bird|man\b|woman|people|farmer|tractor|machine|harvester|combine|market|shop|food|dish|recipe|cooked|soup|salad\b|cake|pie\b|jam\b|bottle|stamp|coin|scan|page|sketch|painting|art\b|poster|disease|damage|infect|rust\b|blight|mildew|pest|microscop|cross.section|seedling tray|logo|icon|x-ray|museum|specimen|dried|seeds? of|banknote',re.I)
LIC=re.compile(r'^(CC BY|CC-BY|CC0|Public domain|PD)',re.I)
def api(p):
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({**p,'format':'json'})
    for t in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except Exception as e: time.sleep(3)
    return {}
def candidates(q):
    d=api({'action':'query','generator':'search','gsrnamespace':6,'gsrsearch':q+' filetype:bitmap','gsrlimit':20,'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':360})
    out=[]
    for p in sorted(d.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',99)):
        t=p['title']; ii=(p.get('imageinfo') or [{}])[0]; md=ii.get('extmetadata',{})
        lic=strip(md.get('LicenseShortName',{}).get('value','')); desc=strip(md.get('ImageDescription',{}).get('value',''))[:300]
        if BAD.search(t) or BAD.search(desc[:120]) or not LIC.match(lic): continue
        if ii.get('width',0)<400 or ii.get('height',0)<300: continue
        out.append(dict(file=t,url=ii.get('thumburl'),page=ii.get('descriptionurl'),author=strip(md.get('Artist',{}).get('value',''))[:120] or 'Unknown',licence=lic))
    return out
def looks_photo(im):
    s=im.convert('L').resize((64,64)); px=list(s.getdata()); white=sum(1 for v in px if v>235)/len(px)
    hsv=im.convert('HSV').resize((64,64)); sat=sum(p[1] for p in hsv.getdata())/4096
    return white<0.35 and sat>35
for c in CROPS:
    i=c['id']
    if ONLY and i not in ONLY: continue
    name=c['n'].split('(')[0].split('—')[0].strip()
    lat=c['lat'].split('/')[0].split(' and ')[0].replace('×','').strip()
    qs=FORCE.get(i,[])+Q.get(i,[])+[f'{name} plant',f'{lat}',name, f'{name} field']
    got=None; seen=set()
    for q in qs:
        if q.startswith('File:'):
            d=api({'action':'query','titles':q,'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':360}); pg=list(d.get('query',{}).get('pages',{}).values())
            if pg and pg[0].get('imageinfo'): ii=pg[0]['imageinfo'][0]; md=ii.get('extmetadata',{}); cands=[dict(file=q,url=ii['thumburl'],page=ii['descriptionurl'],author=strip(md.get('Artist',{}).get('value',''))[:120] or 'Unknown',licence=strip(md.get('LicenseShortName',{}).get('value','')))]
            else: cands=[]
            forced=True
        else: cands=candidates(q); forced=False; time.sleep(0.4)
        for cd in cands[:6]:
            if cd['file'] in seen: continue
            seen.add(cd['file'])
            try:
                raw=urllib.request.urlopen(urllib.request.Request(cd['url'],headers=UA),timeout=30).read(); im=Image.open(io.BytesIO(raw)).convert('RGB')
            except Exception as e: continue
            if not forced and not looks_photo(im): continue
            got=(cd,im); break
            time.sleep(0.3)
        if got: break
    fn=os.path.join(OUT,i+'.webp')
    if not got:
        print('NONE',i,flush=True); cred[i]=None
        if os.path.exists(fn): os.remove(fn)
        continue
    cd,im=got; w,h=im.size; s=min(w,h)
    im=im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)).resize((160,160),Image.LANCZOS); im.save(fn,'WEBP',quality=72,method=6)
    cred[i]=cd; print('OK',i,cd['file'][:70],cd['licence'],flush=True)
    json.dump(cred,open(CRED,'w'),indent=0,ensure_ascii=False)
json.dump(cred,open(CRED,'w'),indent=0,ensure_ascii=False)
