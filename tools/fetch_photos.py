import json,urllib.request,urllib.parse,time,re,io,os,sys
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__))
from crop_list import CROPS
UA={'User-Agent':'FarmhandBuild/1.0 (https://jpfegan1.github.io/farm-app/; farm app crop thumbnails)'}
OUT=os.path.join(os.path.dirname(__file__),'..','crops','img'); os.makedirs(OUT,exist_ok=True)
CRED=os.path.join(os.path.dirname(__file__),'photo_credits.json')
cred=json.load(open(CRED)) if os.path.exists(CRED) else {}
Q={'multispecies':['multispecies sward','chicory plantain clover pasture'],'prg_ley':['Lolium perenne'],'wholecrop_cereal':['whole crop silage','barley field'],
 'arable_silage':['pea barley intercrop','Pisum sativum field'],'cover_mix':['cover crop mixture','cover crop'],'pollinator':['wildflower meadow','wildflower margin'],
 'annual_mix':['cut flower garden','Cosmos bipinnatus'],'hardy_nursery':['plant nursery','tree nursery'],'agroforestry':['silvopasture','agroforestry'],'rowan':['Sorbus aucuparia berries'],
 'microgreens':['microgreens'],'ware_potato':['potato tubers','Solanum tuberosum'],'early_potato':['new potatoes'],'salad_potato':['Charlotte potato','potatoes'],'seed_potato':['seed potatoes'],
 'malting_barley':['barley field','Hordeum vulgare'],'spring_barley':['Hordeum vulgare'],'winter_barley':['barley field'],'forage_maize':['maize field','Zea mays'],'grain_maize':['corn cob','Zea mays'],
 'tomato':['tomatoes Solanum lycopersicum'],'pepper':['Capsicum annuum fruit'],'citrus':['Citrus limon fruit'],'cabbage_spring':['spring greens cabbage','cabbage'],'cabbage_winter':['Savoy cabbage'],
 'kale':['Brassica oleracea kale field'],'christmas_tree':['Abies nordmanniana'],'willow_src':['short rotation coppice willow','Salix viminalis'],'poplar_src':['poplar plantation'],
 'hemp':['industrial hemp field','Cannabis sativa'],'rhubarb_forcing':['forced rhubarb'],'sorrel_herb':['Allium ursinum'],'fennel_herb':['Foeniculum vulgare'],'buckwheat_cover':['buckwheat field'],
 'linseed_cover':['Linum usitatissimum'],'cover_rye':['rye field'],'black_oats':['Avena strigosa'],'tillage_radish':['Raphanus sativus root'],'oil_radish':['oil radish','Raphanus sativus oleiformis'],
 'apple':['Malus domestica apples tree'],'pear':['Pyrus communis fruit'],'hybrid_berry':['tayberry','loganberry'],'redcurrant':['Ribes rubrum'],'onion_sets':['onion sets','Allium cepa'],'onion_seed':['onion bulbs Allium cepa']}
BAD=re.compile(r'map|distribution|herbar|drawing|illustrat|diagram|chart|logo|stamp|\.svg|\.tif|seed packet|plate|kohler|botanical|museum|book|label|sign',re.I)
OK=re.compile(r'^(cc[- ]by(-sa)?[- ]?[0-9.]*|cc0|public domain|pd.*|cc-by-sa-[0-9.]+|cc-by-[0-9.]+)$',re.I)
def api(p):
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({**p,'format':'json'})
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
def strip(h): return re.sub(r'\s+',' ',re.sub('<[^>]+>','',h or '')).strip()
def find(q):
    d=api({'action':'query','generator':'search','gsrnamespace':6,'gsrsearch':q+' filetype:bitmap','gsrlimit':15,'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':360})
    pages=sorted(d.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',99))
    for p in pages:
        t=p['title']; ii=(p.get('imageinfo') or [{}])[0]; md=ii.get('extmetadata',{})
        lic=strip(md.get('LicenseShortName',{}).get('value',''))
        if BAD.search(t) or not OK.match(lic.replace('CC BY-SA','cc-by-sa').replace('CC BY','cc-by')) and not re.match(r'(CC BY|CC0|Public domain|CC-BY)',lic,re.I): continue
        if ii.get('width',0)<300 or ii.get('height',0)<200: continue
        return dict(file=t,url=ii.get('thumburl'),page=ii.get('descriptionurl'),author=strip(md.get('Artist',{}).get('value',''))[:120] or 'Unknown',licence=lic)
def main():
  pass
if __name__=="__main__":
 for c in CROPS:
     i=c['id']; fn=os.path.join(OUT,i+'.webp')
     if i in cred and os.path.exists(fn): continue
     qs=Q.get(i,[])+[c['lat'].split('/')[0].split(' and ')[0].strip(),c['n'].split('(')[0].strip()]
     got=None
     for q in qs:
         try: got=find(q)
         except Exception as e: print('ERR',i,e); time.sleep(3)
         time.sleep(0.6)
         if got: break
     if not got: print('NONE',i); cred[i]=None; continue
     try:
         raw=urllib.request.urlopen(urllib.request.Request(got['url'],headers=UA),timeout=30).read()
         im=Image.open(io.BytesIO(raw)).convert('RGB'); w,h=im.size; s=min(w,h)
         im=im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)).resize((160,160),Image.LANCZOS)
         im.save(fn,'WEBP',quality=72,method=6); cred[i]=got; print('OK',i,got['file'][:60],got['licence'],os.path.getsize(fn))
     except Exception as e: print('DLERR',i,e); cred[i]=None
     json.dump(cred,open(CRED,'w'),indent=0,ensure_ascii=False); time.sleep(0.8)
