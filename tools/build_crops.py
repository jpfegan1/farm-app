import json,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from crop_list import CROPS
from crop_families import F
from varieties import V,ROOT
ROOTD=os.path.join(os.path.dirname(__file__),'..','crops')
cred=json.load(open(os.path.join(os.path.dirname(__file__),'photo_credits.json')))
GROUPS=[('cereals','Cereals'),('oilseeds','Oilseeds & proteins'),('forage','Grass & forage'),('potatoes','Potatoes & field roots'),('vegetables','Vegetables'),
 ('fruit_trees','Fruit trees & nuts'),('soft_fruit','Soft fruit'),('herbs','Herbs'),('energy','Energy & fibre (incl. hemp)'),('cover','Cover crops & green manures'),('flowers','Flowers & nursery'),('forestry','Forestry & hedging')]
SOIL={'l':'light/sandy','m':'medium loam','h':'heavy/clay','p':'peat/organic'}
DR={'free':'Needs free-draining soil','moderate':'Moderately to well drained','tolerant':'Tolerates wetter, poorly drained soil'}
def lime(ph): return f'Lime to keep pH {ph[0]}–{ph[1]}; apply ground limestone per soil test (typically 2.5–7.5 t/ha), ideally a few months before sowing.'
def pk(s): 
    v=s.split('/'); 
    return 'Index 1: %s · Index 2: %s · Index 3: %s · Index 4: %s kg/ha'%tuple(v) if len(v)==4 and s!='0/0/0/0' else 'Normally none required'
groups={g:[] for g,_ in GROUPS}; index=[]
for c in CROPS:
    f=F[c['f']]; ph=c['ph']
    d=dict(id=c['id'],name=c['n'],group=c['g'],latin=c['lat'],overview=c.get('ov',''),ireland=c.get('irl',''),
      soil=dict(types=[SOIL[x] for x in c['soils']],ph=list(ph),drainage=DR[c['dr']],index='Aim for P and K index 3 (Teagasc). Take a soil test every 4–5 years.'),
      planting=dict(window=c['sow'],seed_rate=c['rate'],depth=c['depth'],spacing=c['space'],soil_temp=c['temp']),
      fert=dict(conventional=dict(N=c['N'],P=pk(c['P']),K=pk(c['K']),S='Sulphur 15–25 kg/ha on light soils/high-yield crops' if c['g'] in('cereals','oilseeds','forage') else 'Usually adequate',
                lime=lime(ph),manures='Account for slurry/FYM nutrients (Teagasc Green Book values) and stay within Nitrates Regulations limits (170 kg/ha organic N whole-farm; derogation rules apply).',
                timing='Apply P & K at or before sowing; split N to match crop demand. Observe closed periods for fertiliser and slurry.'),
                organic=dict(text=f['nut_o'],lime=lime(ph))),
      water=dict(rainfall=f['water'],critical=f['critical']),
      harvest=dict(timing=c['hv'],signs=c['sig'],yield_range=c['yld'],storage=f['storage']),
      protect=dict(conventional=dict(pests=f['pests_c'],weeds=f['weeds_c']),organic=dict(pests=f['pests_o'],weeds=f['weeds_o'])),
      rotation=f['rotation'])
    vs=V.get(c['id'],[])
    if vs: d['varieties']=vs
    if c['id'] in ROOT: d['rootstocks']=[dict(name=a,vigour=b,height=h,use=u) for a,b,h,u in ROOT[c['id']]]
    p=cred.get(c['id'])
    if p: d['photo']=dict(img='img/%s.webp'%c['id'],author=p['author'],licence=p['licence'],source=p['page'],file=p['file'])
    groups[c['g']].append(d)
    index.append(dict(id=c['id'],n=c['n'],g=c['g'],lat=c['lat'],ph=list(ph),soils=c['soils'],dr=c['dr'],img=bool(p),vc=len(vs),sow=c['sow']))
for g,_ in GROUPS:
    json.dump(dict(group=g,crops=groups[g]),open(os.path.join(ROOTD,g+'.json'),'w'),ensure_ascii=False,separators=(',',':'))
json.dump(dict(version=1,groups=[dict(id=g,name=n,count=len(groups[g])) for g,n in GROUPS],crops=index,
  credits=[dict(id=i,name=next(c['n'] for c in CROPS if c['id']==i),author=p['author'],licence=p['licence'],source=p['page']) for i,p in cred.items() if p and any(c['id']==i for c in CROPS)]),
  open(os.path.join(ROOTD,'index.json'),'w'),ensure_ascii=False,separators=(',',':'))
nv=sum(len(v) for v in V.values()); ph=sum(1 for x in index if x['img'])
print('crops',len(index),'varieties',nv,'apples',len(V['apple']),'photos %d/%d = %.1f%%'%(ph,len(index),100*ph/len(index)))
print('no photo:',[x['n'] for x in index if not x['img']])
