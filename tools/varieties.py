# Fruit varieties. Pollination group (pg) = RHS flowering group where well documented, else None.
# sf: True self-fertile, 'partly', False needs a pollinator, None not recorded.
import re,html
V={}   # crop_id -> list of dicts
def add(crop,name,use=None,season=None,pg=None,sf=None,disease=None,vigour=None,ireland=None,origin=None,notes=None,**x):
    d=dict(name=name,use=use,season=season,pg=pg,sf=sf,disease=disease,vigour=vigour,ireland=ireland,origin=origin,notes=notes,**x)
    V.setdefault(crop,[]).append({k:v for k,v in d.items() if v is not None})
# --- Irish Seed Savers heritage apple collection (transcribed from their published flowering/pollination table)
import os,json as _j
for c in _j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'issa_apples.json')))['rows'][1:]:
    if len(c)<7 or not c[0]: continue
    n,use,flw,pick,tip,spur,orig=c[:7]
    orig={'Under Research':'Origin under research (ISSA)'}.get(orig,orig)
    bear=' & '.join([b for b,f in (('tip',tip),('spur',spur)) if f.strip()]) or None
    u={'Eater':'Dessert','Cooker':'Culinary','Dual':'Dual purpose'}.get(use,use)
    add('apple',n,use=u,season='Pick '+pick if pick else None,flowering=flw or None,bearing=bear,origin=orig or None,
        ireland=('Irish heritage variety in the Irish Seed Savers collection, grown in Irish conditions' if not re.search(r'U\.?K|England|Somerset|Norfolk|Cambridgeshire',orig or '') else 'Grown in the Irish Seed Savers heritage collection (origin outside Ireland)'),
        heritage=True,src='Irish Seed Savers Association')
A='apple'
for n,use,season,pg,sf,dis,notes in [
 ("Bramley's Seedling",'Culinary','Pick Oct; stores to Mar',3,False,'Moderate scab resistance','Triploid — needs two other pollinators; vigorous. The classic Irish cooker (Armagh Bramley PGI).'),
 ('Discovery','Dessert','Aug–Sept',3,'partly','Good scab & mildew resistance','Reliable early eater; good for Ireland.'),
 ('Egremont Russet','Dessert','Pick late Sept; stores to Dec',2,False,'Scab resistant','Nutty russet; compact tree.'),
 ("Cox's Orange Pippin",'Dessert','Pick Oct; stores to Jan',3,False,'Prone to scab, canker, mildew','Needs warm, dry sites — struggles in wet western areas.'),
 ('James Grieve','Dual purpose','Sept',3,'partly','Prone to canker on wet soil','Good pollinator; reliable.'),
 ('Katy','Dessert','Sept',3,'partly','Fairly healthy','Also sold as Katja; good juicing apple.'),
 ('Worcester Pearmain','Dessert','Sept',3,'partly','Mildew resistant; some scab','Tip-bearer.'),
 ('Sunset','Dessert','Pick Oct; stores to Dec',3,'partly','Better disease resistance than Cox','Cox-like flavour, easier to grow.'),
 ('Spartan','Dessert','Oct–Jan',3,False,'Fairly healthy','Dark red, crisp.'),
 ('Fiesta','Dessert','Pick late Sept; stores to Mar',3,'partly','Fairly healthy','Also sold as Red Pippin.'),
 ('Falstaff','Dessert','Oct–Dec',3,True,'Good resistance; blossom frost-tolerant','Heavy cropper.'),
 ('Red Falstaff','Dessert','Oct–Dec',3,True,'Good resistance','Red sport of Falstaff.'),
 ('Scrumptious','Dessert','Sept',3,True,'Good disease resistance','Good for gardens; no pollinator needed.'),
 ('Saturn','Dessert','Sept–Oct',3,False,'Scab resistant','Modern disease-resistant variety.'),
 ('Redsleeves','Dessert','Aug–Sept',3,False,'Scab & mildew resistant',None),
 ('Grenadier','Culinary','Aug–Sept',3,'partly','Scab resistant','Early cooker; good pollinator.'),
 ('Howgate Wonder','Culinary','Pick Oct; stores to Mar',4,'partly',None,'Very large fruit.'),
 ('Lord Derby','Culinary','Sept–Oct',4,False,'Scab resistant','Tolerates damp, cold sites.'),
 ('Arthur Turner','Culinary','Aug–Oct',3,False,'Scab resistant','Showy blossom.'),
 ('Annie Elizabeth','Culinary','Stores Nov–Apr',4,False,None,'Late-flowering, good for frost pockets.'),
 ('Newton Wonder','Culinary','Stores Nov–Mar',5,False,'Fairly healthy','Vigorous.'),
 ('Blenheim Orange','Dual purpose','Oct–Jan',3,False,'Fairly healthy','Triploid; vigorous, slow to crop.'),
 ('Jupiter','Dessert','Oct–Jan',3,False,None,'Triploid.'),
 ("Ellison's Orange",'Dessert','Sept',4,'partly','Scab resistant; canker on wet soil','Aniseed flavour.'),
 ("Laxton's Superb",'Dessert','Stores Nov–Feb',4,'partly',None,'Biennial tendency.'),
 ('Lord Lambourne','Dessert','Sept–Oct',2,'partly','Fairly healthy','Compact; good for small gardens.'),
 ("Ashmead's Kernel",'Dessert','Stores Dec–Feb',4,False,'Fairly healthy','Russet with intense flavour.'),
 ('Gala','Dessert','Oct',4,False,'Scab prone','Needs a warm site in Ireland.'),
 ('Braeburn','Dessert','Pick late Oct',4,False,None,'Needs a long warm season — marginal in Ireland.'),
 ('Golden Delicious','Dessert','Oct–Jan',4,'partly','Scab prone','Needs warmth.'),
 ('Jonagold','Dessert','Oct–Jan',4,False,None,'Triploid.'),
 ('Elstar','Dessert','Oct–Dec',3,False,None,None),
 ('Herefordshire Russet','Dessert','Oct–Jan',3,True,'Fairly healthy','Self-fertile russet.'),
 ('Charles Ross','Dual purpose','Sept–Oct',3,'partly','Fairly healthy; tolerates chalk',None),
 ('George Cave','Dessert','Aug',2,'partly',None,'Early.'),
 ('Beauty of Bath','Dessert','Early Aug',2,False,None,'Very early; drops fruit.'),
 ('Bountiful','Culinary','Sept–Jan',3,'partly','Mildew resistant','Compact cooker.'),
 ('Reverend W. Wilks','Culinary','Sept–Nov',2,'partly',None,'Compact.'),
 ("Kidd's Orange Red",'Dessert','Nov–Jan',3,False,None,None),
 ('Limelight','Dessert','Sept–Oct',3,'partly','Scab & mildew resistant','Compact; Discovery seedling.'),
 ('Topaz','Dessert','Oct–Jan',None,False,'Scab resistant (Vf gene)','Popular organic variety.'),
 ('Santana','Dessert','Sept–Oct',None,False,'Scab resistant','Tolerated by some apple-allergy sufferers.'),
 ('Christmas Pippin','Dessert','Oct–Jan',3,True,'Good scab resistance','Self-fertile Cox-type.'),
 ("Adams's Pearmain",'Dessert','Stores Dec–Mar',2,False,None,'Tip-bearer.'),
 ('Orleans Reinette','Dessert','Stores Dec–Feb',4,False,None,'Needs warmth.'),
 ('Pixie','Dessert','Stores Dec–Mar',4,False,'Fairly healthy',None),
 ('Crispin','Dual purpose','Oct–Feb',3,False,None,'Also called Mutsu; triploid.'),
 ('Dabinett','Cider (bittersweet)','Nov',None,'partly',None,'Classic cider variety.'),
 ('Michelin','Cider (bittersweet)','Oct–Nov',None,'partly',None,None),
 ('Kingston Black','Cider (bittersharp)','Oct–Nov',None,False,'Scab prone','Single-variety cider classic.'),
 ('Yarlington Mill','Cider (bittersweet)','Oct–Nov',None,False,None,None),
 ("Harry Masters' Jersey",'Cider (bittersweet)','Oct–Nov',None,False,None,None),
 ("Browns",'Cider (sharp)','Oct',None,False,None,None),
 ("Tremlett's Bitter",'Cider (bittersweet)','Oct',None,False,None,None),
 ('John Downie (crab)','Crab / jelly','Sept–Oct',None,None,None,'Ornamental crab, good pollinator.'),
 ('Golden Hornet (crab)','Crab / pollinator','Oct',None,None,None,'Long-flowering crab, pollinator for many apples.'),
 ('Evereste (crab)','Crab / pollinator','Oct',None,None,'Healthy','Very good pollinator.'),
]:
    add(A,name=n,use=use,season=season,pg=pg,sf=sf,disease=dis,notes=notes,origin=None) if False else add(A,n,use=use,season=season,pg=pg,sf=sf,disease=dis,notes=notes)
P='pear'
for n,season,pg,sf,notes in [
 ('Conference','Pick Sept; eat Oct–Nov',3,'partly','The most reliable pear in Ireland.'),('Concorde','Oct–Nov',3,'partly','Compact, reliable.'),
 ('Doyenné du Comice','Oct–Nov',4,False,'Superb flavour; needs a warm wall.'),('Beth','Aug–Sept',4,False,'Early, reliable.'),
 ("Williams' Bon Chrétien",'Aug–Sept',3,'partly','Eat soon after picking.'),('Onward','Sept',4,False,'Comice seedling.'),
 ('Louise Bonne of Jersey','Oct',2,False,None),('Beurré Hardy','Oct',4,False,'Vigorous.'),('Glou Morceau','Stores Dec–Jan',4,False,None),
 ('Durondeau','Oct–Nov',3,'partly',None),('Invincible','Sept–Nov',None,True,'Re-flowers after frost; also called Delwinor.'),
 ('Joséphine de Malines','Stores Dec–Jan',3,False,None),('Merton Pride','Sept',3,False,'Triploid.'),
 ('Catillac','Culinary; stores to Apr',4,False,'Triploid cooking pear.'),('Gorham','Sept',4,False,None),
 ('Black Worcester','Culinary; stores to spring',None,False,'Ancient cooking pear.'),('Hessle','Sept',None,'partly','Hardy northern pear.'),
 ('Fondante d\'Automne','Sept–Oct',None,False,None)]:
    add(P,n,use='Culinary' if 'Culinary' in season else 'Dessert',season=season,pg=pg,sf=sf,notes=notes)
for n in ['Thorn','Blakeney Red','Hendre Huffcap','Moorcroft','Brandy','Gin']:
    add('perry_pear',n,use='Perry',season='Sept–Nov')
for n,notes in [('Shinseiki','Round, crisp, yellow.'),('Kumoi','Russet-brown, crisp.'),('Hosui','Russet, juicy.'),('Nijisseiki','Yellow-green; also "Twentieth Century".')]:
    add('asian_pear',n,use='Dessert',season='Sept',notes=notes)
PL='plum'
for n,use,season,pg,sf,notes in [
 ('Victoria','Dual purpose','Late Aug–Sept',3,True,'Heavy cropper; prone to silver leaf.'),('Czar','Culinary','Early Aug',3,True,'Frost-tolerant flowers; reliable.'),
 ("Marjorie's Seedling",'Dual purpose','Late Sept',5,True,'Late flowering, misses frosts.'),('Opal','Dessert','Late July–Aug',3,True,'Reliable early plum.'),
 ("Denniston's Superb",'Dessert (gage)','Aug',3,True,'Hardy gage; also called Imperial Gage.'),("Rivers's Early Prolific",'Culinary','July–Aug',3,'partly',None),
 ('Jubileum','Dessert','Aug',None,True,'Large Victoria-type.'),('Pershore','Culinary','Aug',3,True,'Yellow Egg plum.'),
 ('Cambridge Gage','Dessert (gage)','Aug–Sept',4,'partly','Best gage for cooler areas.'),('Old Green Gage','Dessert (gage)','Aug',4,False,'Needs warmth.'),
 ('Oullins Gage','Dual purpose','Aug',4,True,None),('Reine Claude de Bavay','Dessert (gage)','Sept',4,True,None),
 ("Coe's Golden Drop",'Dessert','Sept',None,False,None),("Kirke's Blue",'Dessert','Sept',None,False,None),
 ('Warwickshire Drooper','Dual purpose','Sept',None,True,None),('Mirabelle de Nancy','Dual purpose','Aug–Sept',None,True,'Small golden cherry-plum type.'),
 ('Blue Tit','Dual purpose','Aug',None,True,None),('Herman','Dual purpose','July',None,True,'Very early.'),('Excalibur','Dessert','Aug',None,False,'Large red.'),
 ('Belle de Louvain','Culinary','Aug',None,True,None),('Valor','Dessert','Sept',None,'partly',None)]:
    add(PL,n,use=use,season=season,pg=pg,sf=sf,notes=notes)
for n,sf,notes in [('Merryweather',True,'Large-fruited, reliable.'),('Farleigh',True,'Very hardy; good windbreak.'),('Shropshire Prune',True,'Classic flavour; also "Prune Damson".'),('King of Damsons',True,None),('Langley Bullace',True,'Late, very hardy.')]:
    add('damson',n,use='Culinary',season='Sept–Oct',sf=sf,notes=notes)
CH='cherry_sweet'
for n,season,sf,notes in [('Stella','July',True,'First self-fertile sweet cherry.'),('Sunburst','July',True,None),('Lapins','Late July',True,'Crack resistant.'),
 ('Sweetheart','Late July–Aug',True,'Late.'),('Summer Sun','July',True,'Good for cooler areas.'),('Celeste','Early July',True,'Compact.'),('Skeena','Late July',True,'Crack resistant.'),
 ('Merchant','Early July',False,None),('Kordia','July',False,None),('Regina','Late July',False,'Crack resistant.'),('Penny','Late July',False,None),
 ('Van','July',False,None),('Early Rivers','Late June–July',False,None),('Napoleon Bigarreau','July',False,'Old variety.'),('Merton Glory','July',False,None)]:
    add(CH,n,use='Dessert',season=season,sf=sf,notes=notes)
for n,notes in [('Morello','Classic acid cherry — even crops on a north wall.'),('Montmorency',None),('Meteor',None),('Nabella',None)]:
    add('cherry_sour',n,use='Culinary',season='Aug',sf=True,notes=notes)
for n,notes in [('Peregrine','Most reliable outdoor peach in these islands.'),('Rochester',None),('Avalon Pride','Resistant to peach leaf curl.'),('Duke of York',None),('Bellegarde','Late.'),('Saturne','Flat "doughnut" peach.')]:
    add('peach',n,use='Dessert',season='Aug–Sept',sf=True,notes=notes)
for n in ['Lord Napier','Fantasia','Pineapple','Early Rivers']: add('nectarine',n,use='Dessert',season='Aug',sf=True)
for n,notes in [('Moorpark','Old reliable variety.'),('Flavorcot','Late flowering.'),('Tomcot',None),('Goldcot','Hardy.'),('Alfred',None)]:
    add('apricot',n,use='Dessert',season='July–Aug',sf=True,notes=notes)
for n in ["Meech's Prolific",'Vranja','Champion','Portugal','Serbian Gold','Leskovac']: add('quince',n,use='Culinary',season='Oct',sf=True)
for n in ['Nottingham','Royal','Dutch']: add('medlar',n,use='Dessert (bletted)',season='Nov',sf=True)
for n,notes in [('Brown Turkey','Hardiest and most reliable.'),('Brunswick',None),('White Marseilles',None),('Rouge de Bordeaux','Needs cover.')]:
    add('fig',n,use='Dessert',season='Aug–Sept',sf=True,notes=notes)
for n in ['Chelsea','Illinois Everbearing']: add('mulberry',n,use='Dessert',season='Aug–Sept',sf=True)
for n,notes in [('Broadview','Early cropping, compact.'),('Buccaneer','Self-fertile, upright.'),('Franquette','Late leafing.'),('Lara',None),('Fernor','Very late leafing — avoids frost.')]:
    add('walnut',n,use='Nuts',season='Sept–Oct',notes=notes)
for n in ['Kentish Cob','Cosford','Butler','Gunslebert','Ennis',"Webb's Prize Cob","Pearson's Prolific","Hall's Giant"]: add('hazel',n,use='Nuts',season='Sept',sf=False,notes='Plant two varieties for cross-pollination.')
for n in ['Marron de Lyon','Bouche de Bétizac','Marigoule','Belle Épine']: add('sweet_chestnut',n,use='Nuts',season='Oct')
for n in ['Haschberg','Samdal','Samyl']: add('elder',n,use='Flowers & berries',season='Flowers June; berries Aug–Sept')
for n,notes in [('Meyer lemon','Most reliable lemon in a pot.'),('Eureka lemon',None),('Calamondin',None),('Nagami kumquat',None),('Satsuma (Owari)',None),('Washington navel orange',None)]:
    add('citrus',n,use='Fruit',season='Winter',sf=True,notes=notes)
for n,use,notes in [('Phoenix','Wine (white)','Mildew resistant.'),('Solaris','Wine (white)','Very early, disease resistant.'),('Rondo','Wine (red)','Early.'),('Regent','Wine (red)','Disease resistant.'),
 ('Madeleine Angevine','Wine (white)','Early.'),('Seyval Blanc','Wine (white)',None),('Boskoop Glory','Dessert','Outdoor black grape.'),('Black Hamburgh','Dessert','Greenhouse classic.'),('Muscat of Alexandria','Dessert','Heated greenhouse.')]:
    add('grape',n,use=use,season='Sept–Oct',sf=True,notes=notes)
for n,notes in [('Jenny','Self-fertile kiwi.'),('Issai','Self-fertile hardy kiwi berry (A. arguta).')]: add('kiwi',n,use='Fruit',season='Oct',sf=True,notes=notes)
for n,season,notes in [('Elsanta','Mid (June–July)','Commercial standard; prone to mildew.'),('Honeoye','Early (June)',None),('Cambridge Favourite','Mid',None),('Symphony','Late','Good for cooler areas.'),
 ('Florence','Late','Good disease resistance.'),('Malling Centenary','Mid',None),('Sonata','Mid',None),('Christine','Early',None),('Royal Sovereign','Early','Heritage flavour.'),
 ('Malwina','Very late',None),('Albion','Everbearer (June–Oct)',None),('Flamenco','Everbearer',None),('Mara des Bois','Everbearer','Wild-strawberry flavour.'),('Marshmello','Mid',None),('Malling Vibrant','Early',None)]:
    add('strawberry',n,use='Dessert',season=season,sf=True,notes=notes)
for n,season,notes in [('Glen Ample','Mid summer','Spine-free; reliable.'),('Glen Moy','Early summer',None),('Glen Prosen','Mid summer',None),('Glen Fyne','Mid summer',None),('Malling Jewel','Mid summer',None),
 ('Tulameen','Mid–late summer','Large fruit.'),('Octavia','Late summer',None),('Malling Admiral','Late summer',None),('Joan J','Autumn (Aug–Oct)','Primocane; spine-free.'),
 ('Autumn Bliss','Autumn','Primocane.'),('Polka','Autumn','Primocane.'),('All Gold','Autumn','Yellow primocane.'),('Malling Minerva','Early summer',None)]:
    add('raspberry',n,use='Dessert',season=season,sf=True,notes=notes)
for n,notes in [('Ben Connan','Compact; mildew & frost resistant.'),('Ben Lomond','Late flowering.'),('Ben Sarek','Compact.'),('Ben Hope','Resistant to big bud mite.'),('Ben Nevis',None),
 ('Ben Tirran','Late.'),('Big Ben','Large berries.'),('Ebony','Sweet enough to eat fresh.'),('Wellington XXX','Old reliable.'),('Baldwin','Old variety.')]:
    add('blackcurrant',n,use='Culinary/juice',season='July',sf=True,notes=notes)
for n,notes in [('Jonkheer van Tets','Early red.'),('Red Lake','Red.'),('Rovada','Late red, long strigs.'),('Stanza','Red.'),("Laxton's No. 1",'Red.'),('White Versailles','White.'),('Blanka','White.'),('White Grape','White.')]:
    add('redcurrant',n,use='Dessert/culinary',season='July',sf=True,notes=notes)
for n,notes in [('Invicta','Mildew resistant, heavy crops.'),('Hinnonmäki Red','Mildew resistant.'),('Hinnonmäki Yellow','Mildew resistant.'),('Careless','Old culinary.'),('Leveller','Dessert.'),
 ("Whinham's Industry",'Dual; tolerates shade.'),('Pax','Nearly thornless.'),('Captivator','Nearly thornless.'),('Greenfinch','Mildew resistant.'),('Xenia','Large red dessert.')]:
    add('gooseberry',n,use='Dual purpose',season='June–July',sf=True,notes=notes)
for n,season,notes in [('Bluecrop','Mid','Reliable all-rounder.'),('Duke','Early',None),('Patriot','Early',None),('Chandler','Late','Very large berries.'),('Brigitta','Late',None),('Darrow','Late',None),
 ('Northland','Early','Very hardy.'),('Bluegold','Mid',None),('Spartan','Early',None),('Herbert','Late',None),('Goldtraube','Mid',None),('Sunshine Blue','Mid','Compact.'),('Pink Lemonade','Late','Pink berries.')]:
    add('blueberry',n,use='Dessert',season=season,sf='partly',notes=(notes+' ' if notes else '')+'Crops better with a second variety.')
for n,notes in [('Loch Ness','Thornless, upright.'),('Loch Tay','Thornless, early.'),('Chester Thornless','Late.'),('Black Butte','Very large fruit.'),('Helen','Thornless, early.'),
 ('Oregon Thornless',None),('Waldo',None),('Reuben','Primocane.'),('Karaka Black',None),('Navaho','Thornless, erect.')]:
    add('blackberry',n,use='Dessert/culinary',season='July–Sept',sf=True,notes=notes)
for n in ['Tayberry','Loganberry LY654','Boysenberry','Tummelberry','Sunberry']: add('hybrid_berry',n,use='Culinary',season='July–Aug',sf=True)
for n,notes in [('Timperley Early','Early, good for forcing.'),('Victoria','Main crop.'),('Champagne','Early, pink.'),('Stockbridge Arrow','Good for forcing.'),("Glaskin's Perpetual",'Lower oxalic acid.')]:
    add('rhubarb',n,use='Culinary',season='Mar–July',notes=notes)
for n in ['Borealis','Tundra']: add('haskap',n,use='Dessert',season='May–June',sf=False,notes='Needs a compatible second variety.')
for n in ['Viking','Nero']: add('aronia',n,use='Juice/culinary',season='Sept',sf=True)
for k,v in V.items():
    seen=set(); V[k]=[d for d in v if not (d['name'].lower() in seen or seen.add(d['name'].lower()))]
ROOT={'apple':[('M27','Extreme dwarf','1.2–1.8 m','Pots and small gardens; permanent stake; good soil only'),('M9','Dwarf','1.8–2.5 m','Commercial standard; permanent stake'),
 ('M26','Dwarf','2.5–3 m','Small gardens, cordons; stake'),('MM106','Semi-dwarf','3–4 m','Most popular garden rootstock; tolerates most soils'),('MM111','Vigorous','4–5 m','Poorer soils, drier sites, half-standards'),('M25','Very vigorous','5–7 m','Standards, orchards, grazing'),('M116','Semi-dwarf','3–4 m','Phytophthora-resistant alternative to MM106')],
 'pear':[('Quince C','Semi-dwarf','2.5–3 m','Good soils; cordons'),('Quince A','Semi-vigorous','3–4 m','Most garden pears'),('Quince Eline','Dwarf','2–3 m','Hardy, good fruit size'),('Pyrodwarf','Semi-dwarf','3–4 m','Pear rootstock, no incompatibility'),('Pyrus communis (seedling)','Vigorous','6–10 m','Standards and perry pears')],
 'plum':[('Pixy','Dwarf','2–3 m','Small gardens'),('VVA-1','Dwarf','2–3 m','Modern dwarfing'),('St Julien A','Semi-vigorous','3–4 m','Most garden plums, damsons, gages'),('Brompton','Vigorous','4–5 m','Standards'),('Myrobalan B','Vigorous','5–6 m','Standards; tolerant of poor soils')],
 'cherry_sweet':[('Gisela 5','Dwarf','2–3 m','Gardens, pots; good soil'),('Gisela 6','Semi-dwarf','3–4 m','Poorer soils'),('Colt','Semi-vigorous','4–5 m','Fans, gardens'),('F12/1','Vigorous','6+ m','Standards')],
 'peach':[('St Julien A','Semi-vigorous','3–4 m','Fan-trained on walls'),('Pixy','Dwarf','2 m','Patio/pot'),('Montclar','Semi-vigorous','3–4 m','Peach seedling stock')]}
for k in ['damson','cherry_plum']: ROOT[k]=ROOT['plum']
ROOT['cherry_sour']=ROOT['cherry_sweet']; ROOT['nectarine']=ROOT['apricot']=ROOT['peach']
ROOT['quince']=ROOT['medlar']=[('Quince A','Semi-vigorous','3–4 m','Standard choice'),('Quince C','Semi-dwarf','2.5–3 m','Small gardens')]
if __name__=='__main__':
    import collections
    print(sum(len(v) for v in V.values()), {k:len(v) for k,v in V.items()})
