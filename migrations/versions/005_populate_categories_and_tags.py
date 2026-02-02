"""Populate categories and tags

Revision ID: 005
Revises: 004
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime
import re


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def create_slug(name):
    """Create a URL-friendly slug from a name."""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


# Category structure: {category_name: (description, icon, sort_order, [(tag_name, keywords, description)])}
CATEGORY_DATA = {
    "Body Type": {
        "description": "Physical body characteristics and build types",
        "icon": "👤",
        "sort_order": 10,
        "tags": [
            ("BBW", "bbw,big beautiful women,big beautiful woman,curvy,thick,chubby,plus size,voluptuous,heavyset,large,big girls", "Big Beautiful Women - plus size"),
            ("Petite", "petite,small,tiny,short,slim,little,small frame,compact,small girl,spinner,fun size", "Small and slender bodies"),
            ("Tall", "tall,amazon,height,statuesque,long legs,big girl,lengthy,towering,high,giant", "Taller than average height"),
            ("Athletic", "athletic,fit,toned,muscular,sporty,fitness,ripped,buff,strong,lean,gym body", "Fit and athletic builds"),
            ("Slim", "slim,thin,skinny,slender,lean,svelte,trim,lithe,willowy,waif,stick thin", "Slender body type"),
            ("Curvy", "curvy,curves,hourglass,thick,voluptuous,shapely,curvaceous,full figured,busty,thicc", "Pronounced curves"),
            ("PAWG", "pawg,phat ass white girl,thick white girl,big booty white girl,big ass white,white girl ass,thicc white,pawgs", "Phat Ass White Girl"),
            ("SSBBW", "ssbbw,super size bbw,super sized,very large,extremely large,huge,enormous,massive,super fat,ultra bbw", "Super Size Big Beautiful Women"),
            ("Midsize", "midsize,average,normal,medium,regular,standard,typical,moderate,mid sized,medium build", "Average body type"),
            ("Muscular", "muscular,bodybuilder,strong,ripped,buff,jacked,swole,muscle,built,shredded,fitness model", "Muscular physique"),
        ]
    },
    
    "Ethnicity & Skin Color": {
        "description": "Ethnic background and skin tone categories",
        "icon": "🌍",
        "sort_order": 20,
        "tags": [
            ("Asian", "asian,oriental,eastern,japanese,chinese,korean,thai,vietnamese,filipina,asian girl,asian woman", "Asian ethnicity"),
            ("Latina", "latina,latin,hispanic,spanish,mexican,brazilian,colombian,argentinian,puerto rican,south american,central american", "Latina/Hispanic ethnicity"),
            ("Ebony", "ebony,black,african,dark skin,black woman,black girl,chocolate,dark skinned,brown skin,african american", "Dark-skinned/Black"),
            ("White", "white,caucasian,pale,fair skin,european,fair skinned,light skin,white girl,white woman,pale skin", "White/Caucasian"),
            ("Indian", "indian,desi,south asian,hindi,pakistani,bengali,sri lankan,brown,indian girl,indian woman,subcontinental", "Indian/South Asian"),
            ("Middle Eastern", "middle eastern,arab,persian,turkish,arabic,iraqi,iranian,lebanese,syrian,mediterranean,middle east", "Middle Eastern descent"),
            ("Mixed", "mixed,biracial,multiracial,hapa,half asian,blasian,mulatto,mixed race,interracial,eurasian,multi ethnic", "Mixed ethnicity"),
            ("Pale", "pale,fair,light skin,porcelain,white skin,snow white,ivory,milky,alabaster,light skinned,very pale", "Very pale/fair skin"),
            ("Tan", "tan,tanned,bronze,sun kissed,brown,golden,sunkissed,sun tan,dark tan,bronzed,olive skin", "Tanned skin"),
        ]
    },
    
    "Age Group": {
        "description": "Age-related categories (all 18+ only)",
        "icon": "📅",
        "sort_order": 30,
        "tags": [
            ("18-21", "teen,young,18,19,20,21,teenager,young adult,barely legal,just legal,young girl,fresh", "Ages 18-21 only"),
            ("20s", "20s,twenties,young adult,twenty something,in her 20s,twenties girl,mid twenties,late twenties", "In their 20s"),
            ("30s", "30s,thirties,milf,mature,thirty something,in her 30s,thirties woman,mid thirties,late thirties", "In their 30s"),
            ("40+", "40s,40+,mature,older,cougar,over 40,forty plus,forties,50s,fifties,50+", "40 years and older"),
            ("MILF", "milf,mom,mother,mature woman,mommy,soccer mom,hot mom,milfs,mothers,mature milf", "Mothers I'd Like to..."),
            ("GILF", "gilf,granny,grandmother,grandma,senior,old,older woman,gran,nana,mature granny,gilfs", "Grandmothers I'd Like to..."),
            ("College", "college,university,student,campus,coed,college girl,university student,campus girl,schoolgirl,college age", "College age students"),
        ]
    },
    
    "Body Parts": {
        "description": "Focus on specific body parts and features",
        "icon": "💪",
        "sort_order": 40,
        "tags": [
            ("Big Tits", "big tits,large breasts,big boobs,busty,huge tits,massive tits,big breasts,boobs,huge boobs,stacked,big boobies", "Large breasts"),
            ("Small Tits", "small tits,small breasts,tiny tits,little boobs,a cup,flat chest,petite tits,small boobs,little tits,tiny boobs", "Small breasts"),
            ("Big Ass", "big ass,large butt,big booty,thick ass,huge ass,phat ass,fat ass,large booty,big behind,bubble butt,juicy ass", "Large buttocks"),
            ("Small Ass", "small ass,small butt,tiny ass,little butt,tight ass,compact ass,petite ass,small booty,tight butt,little ass", "Small buttocks"),
            ("Legs", "legs,long legs,thighs,calves,gams,stems,pins,leggy,leg,thigh,thick thighs", "Legs focus"),
            ("Feet", "feet,foot,toes,soles,foot fetish,footjob,toe,sole,barefoot,footsie,footworship", "Feet focus"),
            ("Belly", "belly,stomach,tummy,abs,midriff,abdomen,bellybutton,navel,tum,six pack,flat stomach", "Belly/stomach"),
            ("Pussy", "pussy,vagina,vulva,cunt,lips,kitty,vag,puss,box,beaver,snatch", "Vagina focus"),
            ("Cock", "cock,dick,penis,shaft,member,rod,meat,johnson,tool,prick,package", "Penis focus"),
            ("Ass", "ass,butt,booty,behind,bum,rear,rump,backside,bottom,derriere,cheeks", "Buttocks focus"),
            ("Nipples", "nipples,nipple,nips,areola,tit,tits,nip,teats,breast,boob,titty", "Nipple focus"),
            ("Lips", "lips,mouth,blowjob lips,cocksucking lips,dsl,dick sucking lips,puffy lips,full lips,pouty lips,oral,kisser", "Mouth/lips focus"),
        ]
    },
    
    "Hair Color": {
        "description": "Hair color and style categories",
        "icon": "💇",
        "sort_order": 50,
        "tags": [
            ("Blonde", "blonde,blond,fair hair,golden,platinum,platinum blonde,bleached,blondie,golden hair,light hair,yellow hair", "Blonde hair"),
            ("Brunette", "brunette,brown hair,brown,dark hair,chocolate,chestnut,dark brown,light brown,mousy,brunettes", "Brown hair"),
            ("Redhead", "redhead,ginger,red hair,auburn,red,copper,strawberry blonde,carrot top,fire,flame,gingers", "Red hair"),
            ("Black Hair", "black hair,dark hair,raven,jet black,ebony hair,dark,black,noir,raven hair,jet", "Black hair"),
            ("Dyed", "dyed,colored,rainbow,pink,blue,purple,green,colorful,neon,alternative,emo,scene,multicolor", "Dyed/colored hair"),
            ("Bald", "bald,shaved head,no hair,skinhead,chrome dome,baldy,hairless,smooth head,buzzed,buzz cut", "No hair/bald"),
        ]
    },
    
    "Sexual Positions": {
        "description": "Common sexual positions",
        "icon": "🔄",
        "sort_order": 60,
        "tags": [
            ("Doggy Style", "doggy,doggy style,from behind,doggystyle,doggie,doggie style,rear entry,behind,all fours,bent over,dog style", "Doggy style position"),
            ("Missionary", "missionary,mish,face to face,on back,traditional,man on top,classic,missionary position,face-to-face,standard", "Missionary position"),
            ("Cowgirl", "cowgirl,riding,on top,girl on top,ride,woman on top,reverse cowgirl,rider,cow girl,bouncing,riding cock", "Cowgirl/riding position"),
            ("Reverse Cowgirl", "reverse cowgirl,reverse,reverse riding,backwards,reverse cow,rev cowgirl,backwards riding,reverse ride,backwards cowgirl", "Reverse cowgirl"),
            ("69", "69,sixty nine,mutual oral,69ing,mutual,reciprocal,sixty-nine,sixnine,6-9,oral both", "69 position"),
            ("Standing", "standing,standing sex,stand,stand and carry,standing fuck,vertical,upright,stand up,against wall", "Standing position"),
            ("Spooning", "spooning,side by side,on side,spoon,side entry,sideways,side fuck,lateral,cuddle fuck", "Spooning position"),
            ("Prone Bone", "prone bone,prone,flat on stomach,pronebone,prone position,flat,stomach down,prone fuck,laying flat", "Prone bone position"),
        ]
    },
    
    "Sexual Acts": {
        "description": "Specific sexual activities and acts",
        "icon": "🔥",
        "sort_order": 70,
        "tags": [
            ("Blowjob", "blowjob,bj,oral,fellatio,sucking,cock sucking,head,blow job,giving head,suck,cocksuck,deepthroat", "Oral sex on male"),
            ("Cunnilingus", "cunnilingus,eating out,pussy licking,oral,licking,going down,eat out,eating pussy,muff diving,tongue,carpet munching", "Oral sex on female"),
            ("Anal", "anal,butt sex,anal sex,ass fuck,backdoor,anal play,buttfuck,ass,booty,sodomy,up the ass", "Anal sex"),
            ("Creampie", "creampie,cum inside,internal cumshot,cream pie,filled,dripping,cum drip,internal,breeding,insemination,finish inside", "Internal ejaculation"),
            ("Cumshot", "cumshot,facial,cum,ejaculation,money shot,cum shot,finish,pop,blast,nut,jizz", "External ejaculation"),
            ("Squirting", "squirting,squirt,ejaculation,gushing,female ejaculation,spray,wet,fountain,splash,waterworks,pussy juice", "Female ejaculation"),
            ("Deepthroat", "deepthroat,deep throat,throat fuck,gagging,gag,facefuck,face fuck,throat,balls deep,all the way,choking", "Deep oral penetration"),
            ("Titfuck", "titfuck,tit fuck,boob job,titty fuck,titjob,tit job,boobjob,breast fuck,tit wank,motorboat,between tits", "Breast sex"),
            ("Handjob", "handjob,hand job,manual,jerking,jerk off,hand,stroking,tug,stroke,wank,beating off", "Manual stimulation"),
            ("Fingering", "fingering,finger,digital,finger fuck,fingerbang,digits,fingered,finger bang,manual,hand,touch", "Digital penetration"),
            ("Double Penetration", "dp,double penetration,double,two holes,dvp,dap,double stuff,both holes,dual penetration,two cocks,dvda", "Two penetrations simultaneously"),
            ("Fisting", "fisting,fist,extreme,hand,punch,wrist,arm,extreme penetration,fisted,whole hand,stretch", "Fist penetration"),
        ]
    },
    
    "Kinks & Fetishes": {
        "description": "Specific kinks, fetishes and alternative practices",
        "icon": "⛓️",
        "sort_order": 80,
        "tags": [
            ("BDSM", "bdsm,bondage,discipline,dominance,submission,kink,sadomasochism,s&m,sm,dungeon,kinky,fetish", "BDSM activities"),
            ("Bondage", "bondage,tied up,rope,restraints,bound,tied,ropes,restraint,bound and gagged,strapped,hogtied,shibari", "Restraint/bondage"),
            ("Domination", "domination,dom,dominant,control,master,mistress,dominatrix,domme,dominating,power,authority,femdom", "Dominance/control"),
            ("Submission", "submission,sub,submissive,obedient,slave,servant,bottom,subby,serve,owned,pet,surrender", "Submission"),
            ("Roleplay", "roleplay,role play,fantasy,scenario,pretend,acting,play,costume,character,dress up,cosplay", "Roleplay scenarios"),
            ("Voyeur", "voyeur,watching,spy,hidden,peeping,peep,watch,observe,spectator,viewer,voyeurism,candid", "Watching others"),
            ("Exhibition", "exhibition,public,flash,showing off,exhibitionist,outdoor,outside,exposed,display,flashing,nude in public", "Public display"),
            ("Bukkake", "bukkake,group cum,multiple cumshots,facial,cum bath,cum shower,gang facial,multiple men,group facial,covered in cum", "Multiple partners cumming on one"),
            ("Gangbang", "gangbang,gang bang,group,multiple partners,train,running train,group sex,gang,multiple men,several guys,group fuck", "Multiple partners with one"),
            ("Incest", "incest,family,taboo,related,roleplay,step,stepsis,stepmom,forbidden,faux,fauxcest,family roleplay", "Family roleplay fantasy"),
            ("Cuckold", "cuckold,cuck,hotwife,sharing,wife sharing,cuckolding,shared wife,bull,stag,watching wife,cheating wife", "Cuckold scenarios"),
            ("Pegging", "pegging,strap on,strapon,female dom,femdom,dildo,reverse,woman fucks man,strap,girl fucks guy,anal play", "Female penetrating male with strap-on"),
            ("Feet Fetish", "feet,foot fetish,toes,soles,worship,footjob,foot,toe,barefoot,foot worship,footsie,foot slave", "Foot fetish"),
            ("Latex", "latex,rubber,pvc,leather,shiny,fetish wear,catsuit,bodysuit,glossy,vinyl,spandex,tight", "Latex/rubber materials"),
            ("Humiliation", "humiliation,degradation,shame,embarrassment,degrading,humiliate,sph,small penis humiliation,verbal,insult,mock", "Humiliation play"),
        ]
    },
    
    "Participants": {
        "description": "Number and type of participants",
        "icon": "👥",
        "sort_order": 90,
        "tags": [
            ("Solo Female", "solo,solo female,masturbation,alone,self,solo girl,touching herself,self pleasure,solo woman,by herself,lone", "Single female"),
            ("Solo Male", "solo male,male masturbation,jerking,jerk off,alone male,solo guy,self pleasure,solo man,guy alone,beating off", "Single male"),
            ("Couple", "couple,mf,straight,heterosexual,boyfriend,girlfriend,two,pair,duo,twosome,partners", "Male/female couple"),
            ("Lesbian", "lesbian,ff,girl on girl,wlw,women loving women,girls,two girls,sapphic,lesbians,girl girl,dyke", "Female/female"),
            ("Gay", "gay,mm,male on male,mlm,men loving men,guys,two guys,homosexual,gay sex,boy boy,queer", "Male/male"),
            ("Threesome", "threesome,3some,three,three people,trio,three way,threeway,triple,three person,3 way,triad", "Three participants"),
            ("Foursome", "foursome,4some,four,four people,quad,four way,fourway,quadruple,four person,4 way,quartet", "Four participants"),
            ("Orgy", "orgy,group sex,multiple,many people,gang,group,mass,many,several,numerous,crowd", "Large group"),
            ("MFF", "mff,two girls one guy,three way,2 girls,ffm,devil's threesome,one guy two girls,dual girls,girls sharing", "Male with two females"),
            ("MMF", "mmf,two guys one girl,three way,spit roast,dp,mfm,2 guys,devil's threesome,one girl two guys,eiffel tower", "Two males with female"),
            ("Trans", "trans,transgender,ts,tg,shemale,ladyboy,tranny,transsexual,tgirl,trans woman,trans man,transexual", "Transgender participants"),
        ]
    },
    
    "Sexual Orientation": {
        "description": "Sexual orientation categories",
        "icon": "🏳️‍🌈",
        "sort_order": 100,
        "tags": [
            ("Straight", "straight,heterosexual,het,mf,hetero,opposite sex,male female,straight sex,conventional,traditional", "Heterosexual content"),
            ("Lesbian", "lesbian,wlw,sapphic,girl on girl,female homosexual,dyke,women loving women,girls only,ff,gay women", "Female homosexual"),
            ("Gay", "gay,mlm,homosexual,male on male,men loving men,guys only,mm,queer,gay men,same sex", "Male homosexual"),
            ("Bisexual", "bisexual,bi,both,switch,both sexes,bi sexual,pansexual,swing both ways,both ways,flexible", "Bisexual content"),
        ]
    },
    
    "Relationship Type": {
        "description": "Relationship status and production type",
        "icon": "💑",
        "sort_order": 110,
        "tags": [
            ("Amateur", "amateur,homemade,real,couple,genuine,home video,real couple,non professional,authentic,user submitted,home made", "Amateur/homemade content"),
            ("Professional", "professional,pro,pornstar,produced,studio,porn star,commercial,professional porn,industry,paid,produced porn", "Professional content"),
            ("Girlfriend", "girlfriend,gf,significant other,partner,girl friend,babe,honey,sweetheart,lover,my girl", "Girlfriend content"),
            ("Wife", "wife,married,spouse,wifey,hubby,matrimony,wedded,mrs,better half,old lady,married woman", "Wife content"),
            ("Cheating", "cheating,affair,unfaithful,sneaky,infidelity,cheat,adultery,secret,behind back,two timing,forbidden", "Infidelity themed"),
            ("Stranger", "stranger,random,unknown,pickup,picked up,meet,one night stand,hookup,anonymous,casual,first time meeting", "Strangers/casual encounters"),
        ]
    },
    
    "Appearance & Style": {
        "description": "Appearance, clothing, and styling features",
        "icon": "👗",
        "sort_order": 120,
        "tags": [
            ("Clothed", "clothed,dressed,wearing,clothes on,clothed sex,partially clothed,half dressed,still dressed,wearing clothes,in clothes", "Clothed/partially clothed"),
            ("Naked", "naked,nude,stripped,bare,unclothed,no clothes,undressed,birthday suit,in the buff,au naturel,starkers", "Fully nude"),
            ("Lingerie", "lingerie,underwear,bra,panties,sexy clothes,lace,teddy,corset,negligee,undergarments,intimates", "Lingerie"),
            ("Stockings", "stockings,pantyhose,nylons,tights,hosiery,thigh highs,fishnets,hold ups,stay ups,garter,leggings", "Stockings/hosiery"),
            ("Uniform", "uniform,costume,outfit,dress up,cosplay,maid,nurse,schoolgirl,police,military,work clothes", "Uniforms/costumes"),
            ("Glasses", "glasses,specs,spectacles,nerdy,nerd,four eyes,eyeglasses,frames,wearing glasses,geek,librarian", "Wearing glasses"),
            ("Tattoo", "tattoo,tattooed,ink,inked,body art,tats,tatted,tattoos,tat,marked,skin art", "Tattooed"),
            ("Piercing", "piercing,pierced,body piercing,piercings,nipple piercing,belly piercing,rings,studs,pierced nipples,metal", "Body piercings"),
            ("Hairy", "hairy,bush,natural,unshaved,fuzzy,hairy pussy,hairy body,hair,au naturel,untrimmed,full bush", "Natural/hairy"),
            ("Shaved", "shaved,smooth,hairless,bare,waxed,clean,bald,trimmed,groomed,shaven,no hair", "Shaved/smooth"),
            ("Tan Lines", "tan lines,tan,bikini lines,pale lines,farmer tan,tan line,bikini tan,contrast,marks,lines", "Visible tan lines"),
            ("Goth", "goth,gothic,emo,alternative,dark,black,scene,punk,alt,dark makeup,pale goth", "Goth/alternative style"),
            ("Yoga Pants", "yoga pants,leggings,tight pants,lycra,spandex,workout pants,gym pants,athletic wear,stretchy pants,activewear", "Yoga pants/leggings"),
        ]
    },
    
    "Location & Setting": {
        "description": "Where the content takes place",
        "icon": "📍",
        "sort_order": 130,
        "tags": [
            ("Bedroom", "bedroom,bed,home,private,boudoir,sleeping,room,in bed,on bed,master bedroom,guest room", "Bedroom setting"),
            ("Public", "public,outside,outdoor,risky,in public,outdoors,open air,public place,publicly,exhibition,exposed", "Public places"),
            ("Bathroom", "bathroom,shower,bath,toilet,restroom,bathtub,tub,washroom,lavatory,shower sex,bathing", "Bathroom"),
            ("Beach", "beach,ocean,sand,seaside,shore,coast,waterfront,beachside,sandy,waves,surf", "Beach/ocean"),
            ("Car", "car,vehicle,driving,backseat,auto,automobile,in car,car sex,parking,parked,road trip", "In vehicle"),
            ("Office", "office,work,desk,workplace,work place,conference room,cubicle,at work,professional,corporate,building", "Office/workplace"),
            ("Gym", "gym,workout,fitness center,locker room,exercise,fitness,health club,weight room,training,working out", "Gym/fitness center"),
            ("Kitchen", "kitchen,cooking,counter,table,dining,food,sink,pantry,dinner,culinary,breakfast", "Kitchen"),
            ("Pool", "pool,swimming,water,wet,poolside,swimming pool,jacuzzi,hot tub,spa,in pool,underwater", "Pool/swimming"),
            ("Nature", "nature,forest,woods,outdoor,camping,hiking,wilderness,trees,outdoors,park,wild", "Outdoor nature"),
        ]
    },
    
    "Camera & Format": {
        "description": "How content is captured and presented",
        "icon": "📹",
        "sort_order": 140,
        "tags": [
            ("POV", "pov,point of view,first person,pov porn,first-person,subjective,your pov,from your view,pov angle,perspective", "Point of view camera"),
            ("Selfie", "selfie,self shot,mirror,phone,self pic,self portrait,self taken,mirror pic,bathroom selfie,mirror selfie", "Self-taken photos/videos"),
            ("Candid", "candid,caught,unaware,spy,hidden,secret,caught on camera,unknowing,unposed,natural,spontaneous", "Candid/unposed"),
            ("Posed", "posed,professional,staged,modeled,modeling,posing,set up,arranged,photoshoot,studio,planned", "Posed shots"),
            ("GIF", "gif,animated,animation,loop,moving,looping,short clip,animated gif,repeating,motion,cinemagraph", "Animated GIFs"),
            ("Video", "video,clip,movie,film,footage,recording,motion picture,vid,streaming,play,moving picture", "Video content"),
            ("Photo", "photo,pic,picture,image,still,photograph,snapshot,shot,photography,jpeg,png", "Photo/still image"),
            ("Verification", "verification,verified,real,authentic,confirmed,prove,proof,verify,legitimate,genuine,certified", "Verified real people"),
        ]
    },
    
    "Special Features": {
        "description": "Unique characteristics or themes",
        "icon": "⭐",
        "sort_order": 150,
        "tags": [
            ("Celebrity", "celebrity,famous,star,porn star,celeb,celebrities,well known,popular,pornstar,name,recognizable", "Celebrities/famous people"),
            ("Cosplay", "cosplay,costume,character,anime,game,comic,superhero,character costume,dress up,fictional,fantasy costume", "Cosplay/character costumes"),
            ("Pregnant", "pregnant,pregnancy,expecting,baby bump,preggo,knocked up,gravid,with child,maternity,preggers,nine months", "Pregnant"),
            ("Lactating", "lactating,breast milk,nursing,milky,milk,breastfeeding,lactation,milking,producing milk,nursing mom", "Lactation"),
            ("Hentai", "hentai,anime,manga,drawn,cartoon,animated,ecchi,doujin,japanese animation,hentai anime,2d", "Anime/manga style"),
            ("Vintage", "vintage,retro,old,classic,70s,80s,90s,throwback,old school,historical,antique,classic porn", "Vintage/retro"),
            ("Interracial", "interracial,mixed,different races,inter racial,multiracial,race mixing,black and white,bwc,bbc,racial", "Interracial content"),
            ("Barely Legal", "barely legal,18,young,teen,just legal,just 18,fresh,newly legal,legal teen,young adult,new", "Just turned 18"),
            ("Extreme", "extreme,hardcore,intense,rough,hard,brutal,rough sex,aggressive,violent,forceful,wild", "Extreme/hardcore"),
        ]
    },
    
    "Geographic Location": {
        "description": "Geographic origin of content or participants",
        "icon": "🌎",
        "sort_order": 160,
        "tags": [
            ("USA", "usa,american,america,united states,us,americano,yankee,states,u.s.,american girl,us girl", "United States"),
            ("UK", "uk,british,england,britain,english,great britain,brit,united kingdom,scottish,welsh,irish", "United Kingdom"),
            ("Europe", "europe,european,eu,continental,euro,scandinavia,scandinavian,nordic,western europe,eastern europe", "European"),
            ("Asia", "asia,asian,eastern,orient,oriental,far east,southeast asia,east asia,south asia,asian region", "Asian region"),
            ("Latin America", "latin america,south america,latino,latina,central america,hispanic,latin,southamerican,latinoamerica", "Latin American"),
            ("Australia", "australia,australian,aussie,down under,oz,oceania,new zealand,kiwi,pacific,antipodean", "Australian/Oceania"),
            ("Canada", "canada,canadian,maple,canuck,quebec,ontario,canadian girl,canadian woman,north america,ca", "Canadian"),
            ("Russia", "russia,russian,slavic,eastern europe,soviet,cyrillic,moscow,slav,russian girl,russian woman,ruski", "Russian"),
            ("Japan", "japan,japanese,jav,nippon,nihon,tokyo,osaka,japanese girl,japanese woman,j-girl,asian japanese", "Japanese"),
            ("Korea", "korea,korean,hangul,seoul,k-pop,korean girl,korean woman,kpop,south korea,k-girl,asian korean", "Korean"),
        ]
    },
}


def upgrade():
    """Populate categories and tags."""
    connection = op.get_bind()
    
    print("Starting category and tag population...")
    
    for category_name, category_data in CATEGORY_DATA.items():
        # Check if category exists by name
        result = connection.execute(
            sa.text("SELECT id FROM category WHERE name = :name"),
            {"name": category_name}
        )
        row = result.fetchone()
        
        if row:
            category_id = row[0]
            print(f"Category '{category_name}' already exists with id={category_id}")
        else:
            # Insert category and get the new ID
            result = connection.execute(
                sa.text("""
                    INSERT INTO category (name, slug, description, icon, sort_order, active, created_at)
                    VALUES (:name, :slug, :description, :icon, :sort_order, :active, :created_at)
                    RETURNING id
                """),
                {
                    "name": category_name,
                    "slug": create_slug(category_name),
                    "description": category_data.get("description"),
                    "icon": category_data.get("icon"),
                    "sort_order": category_data.get("sort_order", 0),
                    "active": True,
                    "created_at": datetime.utcnow()
                }
            )
            category_id = result.scalar()
            print(f"Created category '{category_name}' with id={category_id}")
        
        # Insert tags for this category
        for tag_data in category_data.get("tags", []):
            tag_name, keywords, description = tag_data
            
            # Check if tag exists
            result = connection.execute(
                sa.text("SELECT id FROM category_tag WHERE category_id = :cat_id AND name = :name"),
                {"cat_id": category_id, "name": tag_name}
            )
            row = result.fetchone()
            
            if row:
                print(f"  Tag '{tag_name}' already exists")
            else:
                # Insert tag
                connection.execute(
                    sa.text("""
                        INSERT INTO category_tag (category_id, name, slug, keywords, description, sort_order, active, created_at)
                        VALUES (:category_id, :name, :slug, :keywords, :description, :sort_order, :active, :created_at)
                    """),
                    {
                        "category_id": category_id,
                        "name": tag_name,
                        "slug": create_slug(tag_name),
                        "keywords": keywords,
                        "description": description,
                        "sort_order": 0,
                        "active": True,
                        "created_at": datetime.utcnow()
                    }
                )
                print(f"  Created tag '{tag_name}'")


def downgrade():
    """Remove all categories and tags."""
    op.execute("DELETE FROM subreddit_category_tag")
    op.execute("DELETE FROM category_tag")
    op.execute("DELETE FROM category")
