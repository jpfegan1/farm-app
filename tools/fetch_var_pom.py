# Second source for variety images: USDA Pomological Watercolor Collection on Wikimedia Commons (public domain, 1886–1942).
# A file is accepted only if its description reads "Image of the <variety> variety of peaches|nectarines".
import json,urllib.request,urllib.parse,time,re,io,os,sys,unicodedata
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__))
from fetch_photos import UA, strip
import stone_fruit as SF
OUT=os.path.join(os.path.dirname(__file__),'..','crops','img')
CRED=os.path.join(os.path.dirname(__file__),'var_pom_credits.json')
cred=json.load(open(CRED)) if os.path.exists(CRED) else {}
def slug(s): return re.sub(r'[^a-z0-9]+','_',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('_')
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
ALIAS={"Hale's Early":["Hale Early","Hales Early","Hale's Early"],'Early Rivers (peach)':['Early Rivers','Rivers'],'Salwey':['Salway','Salwey'],
 'J. H. Hale':['J. H. Hale','J.H. Hale'],'The Nectarine Peach':['Nectarine Peach'],'Salish Summer (Q-1-8)':[],"Rivers' Early York":["Rivers Early York"],
 'Belle of Georgia':['Belle','Belle of Georgia'],'Oldmixon Free':['Oldmixon Free','Old Mixon Free'],'Oldmixon Cling':['Oldmixon Cling','Old Mixon Cling'],
 "O'Henry":["O'Henry",'OHenry'],'Dr Hogg':['Dr. Hogg','Doctor Hogg'],"Rivers's White":['Rivers White'],"Hunt's Tawny":['Hunts Tawny',"Hunt's Tawny"],'Snow Queen':['Snow Queen'],'All Star':['Allstar','All Star']}
def api(p):
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({**p,'format':'json'})
    for t in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except Exception: time.sleep(3)
    return {}
for crop,L in (('peach',SF.PEACH),('nectarine',SF.NECT)):
    fw='peaches' if crop=='peach' else 'nectarines'
    for v in L:
        key=f'{crop}/{v["name"]}'
        if key in cred: continue
        names=ALIAS.get(v['name'],[v['name']]); got=None
        for nm in names:
            d=api({'action':'query','generator':'search','gsrnamespace':6,'gsrsearch':f'"Image of the {nm} variety of {fw}"','gsrlimit':10,'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':400})
            time.sleep(0.4)
            pages=sorted(d.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',99))
            for p in pages:
                ii=(p.get('imageinfo') or [{}])[0]; md=ii.get('extmetadata',{})
                desc=strip(md.get('ImageDescription',{}).get('value',''))
                m=re.search(r'Image of the (.+?) variety of (peaches|nectarines)',desc)
                if not m or m.group(2)!=fw or norm(m.group(1))!=norm(nm): continue
                lic=strip(md.get('LicenseShortName',{}).get('value',''))
                if not re.match(r'(Public domain|PD|CC0)',lic,re.I): continue
                got=dict(file=p['title'],url=ii.get('thumburl'),page=ii.get('descriptionurl'),author=strip(md.get('Artist',{}).get('value',''))[:120] or 'USDA Pomological Watercolor Collection',
                         licence=lic,kind='illustration',date=strip(md.get('DateTimeOriginal',{}).get('value',''))[:40],desc=desc[:200]); break
            if got: break
        if not got: cred[key]=None; print('NONE',key,flush=True)
        else:
            try: im=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(got['url'],headers=UA),timeout=30).read())).convert('RGB')
            except Exception as e: print('ERR',key,e); continue
            w,h=im.size; s=min(w,h); im=im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)).resize((160,160),Image.LANCZOS)
            fn=f'var_{crop}_{slug(v["name"])}_pom.webp'; im.save(os.path.join(OUT,fn),'WEBP',quality=74,method=6)
            got['img']='img/'+fn; cred[key]=got; print('OK',key,'|',got['file'],'|',got['author'][:40],got['date'],flush=True)
        json.dump(cred,open(CRED,'w'),indent=0,ensure_ascii=False)
