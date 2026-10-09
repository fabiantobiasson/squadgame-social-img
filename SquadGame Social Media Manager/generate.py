#!/usr/bin/env python3
"""SquadGame inläggsgenerator. Kör: python3 generate.py  -> skapar PNG i out/ och captions.md"""
import os, html, json
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
CHROME = '/opt/pw-browsers/chromium'

CSS = """
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1350px;background:#1a3d38;font-family:"Helvetica Neue",Arial,sans-serif;color:#F1ECE1;position:relative;overflow:hidden}
.glow{position:absolute;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(230,180,34,.22),transparent 65%);top:-250px;right:-250px}
.logo{position:absolute;top:60px;left:70px;width:96px;height:96px;border-radius:22px}
.tag{position:absolute;top:84px;right:70px;font-size:30px;letter-spacing:6px;color:#e6b422;font-weight:700}
h1{position:absolute;top:190px;left:70px;right:70px;font-size:92px;line-height:1.04;font-weight:900;letter-spacing:-2px}
h1 span,.gold{color:#e6b422}
p.sub{position:absolute;top:510px;left:70px;width:880px;font-size:40px;line-height:1.35;opacity:.85}
.grid{position:absolute;top:670px;left:70px;right:70px;display:grid;grid-template-columns:1fr 1fr;gap:28px}
.card{background:rgba(241,236,225,.08);border:2px solid rgba(230,180,34,.45);border-radius:32px;padding:28px 36px;height:215px}
.card .i{font-size:56px}.card b{display:block;font-size:40px;margin:8px 0 6px;color:#e6b422}
.card small{font-size:28px;opacity:.75}
.cta{position:absolute;bottom:70px;left:70px;right:70px;display:flex;justify-content:space-between;align-items:center;border-top:2px solid rgba(241,236,225,.25);padding-top:36px}
.cta .l{font-size:38px;font-weight:700}.cta .r{font-size:34px;color:#e6b422;font-weight:700}
.big{position:absolute;top:200px;left:70px;font-size:360px;font-weight:900;color:#e6b422;line-height:1;letter-spacing:-10px}
.tip-t{position:absolute;top:610px;left:70px;right:70px;font-size:84px;line-height:1.05;font-weight:900;letter-spacing:-2px}
.tip-b{position:absolute;top:900px;left:70px;width:900px;font-size:44px;line-height:1.38;opacity:.88}

.phone{position:absolute;left:50%;transform:translateX(-50%);top:640px;width:560px;height:760px;border-radius:64px 64px 0 0;background:#0f2623;border:10px solid #0b1d1a;border-bottom:none;overflow:hidden;box-shadow:0 0 0 3px rgba(230,180,34,.5),0 30px 80px rgba(0,0,0,.5)}
.phone img{width:100%;display:block}
h1.s{font-size:84px;top:180px}
p.sub.s{top:480px;font-size:38px;width:900px}
.swipe{position:absolute;bottom:70px;right:70px;font-size:34px;color:#e6b422;font-weight:700}
.dots{position:absolute;bottom:80px;left:70px;font-size:30px;opacity:.7;letter-spacing:4px}
"""

def page(body):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="glow"></div><img class="logo" src="assets/logo.png"><div class="tag">SQUADGAME</div>{body}</body></html>'

def cards(items):
    return '<div class="grid">' + ''.join(f'<div class="card"><div class="i">{i}</div><b>{html.escape(t)}</b><small>{html.escape(s)}</small></div>' for i,t,s in items) + '</div>'

def hero(title_html, sub, items, left="Fotbollsappen för ditt lag", right="squadgame.se →"):
    return page(f'<h1>{title_html}</h1><p class="sub">{html.escape(sub)}</p>{cards(items)}<div class="cta"><div class="l">{html.escape(left)}</div><div class="r">{html.escape(right)}</div></div>')

def phone(title_html, sub, img):
    return page(f'<h1 class="s">{title_html}</h1><p class="sub s">{html.escape(sub)}</p><div class="phone"><img src="assets/{img}"></div>')

def cover(title_html, sub):
    return page(f'<h1 style="top:300px;font-size:104px">{title_html}</h1><p class="sub" style="top:760px">{html.escape(sub)}</p><div class="swipe">Svep →</div>')

def tip(n, title, body, total):
    return page(f'<div class="big">{n}</div><div class="tip-t">{html.escape(title)}</div><div class="tip-b">{html.escape(body)}</div><div class="dots">{n} / {total}</div>')

def outro():
    return page('<h1 style="top:300px">Vill ni testa med <span>laget?</span></h1><p class="sub" style="top:640px">Gratis att komma igång. Läs mer på squadgame.se eller skicka ett DM.</p><div class="cta"><div class="l">Fotbollsappen för ditt lag</div><div class="r">squadgame.se →</div></div>')

HASH_MAIN = "#ungdomsfotboll #fotbollslag #fotbollsapp #lagkänsla #squadgame"

POSTS = [
 {"id":"01-matchens-lirare","slides":[hero("Matchens lirare<br>avgörs av <span>laget</span>","Efter varje match röstar ni fram den som var bäst. Nedräkning, live-resultat och en vinnare som utses automatiskt.",[("⭐","Rösta","på bästa lagkamraten"),("⏱️","Nedräkning","så ingen missar det"),("📊","Live-resultat","medan ni röstar"),("🏆","Vinnare","utses automatiskt")])],
  "caption":"Vem var egentligen bäst i går? ⚽\n\nI SquadGame röstar hela laget fram matchens lirare efter varje match. Det finns en nedräkning, resultatet syns live och vinnaren utses automatiskt.\n\nTagga lagkompisen som alltid tar hem det. 👇","hash":HASH_MAIN+" #matchenslirare"},
 {"id":"02-boter","slides":[hero("Kom försent<br>till träning?<br><span>Laget vet redan.</span>","Ett rättvist bötessystem med lagets egna regler. Betala via Swish och se vad som ligger i lagkassan.",[("⏰","Försent","till träning"),("🎽","Glömd utrustning","hemma i hallen"),("📵","Missad träning","utan att höra av sig"),("💰","Lagkassan","alltid synlig")])],
  "caption":"Försent, glömd utrustning eller missat träning utan att säga till? 😅\n\nMed böter i SquadGame sätter laget sina egna regler, och lagkassan syns för alla. Betalning går via Swish om laget har ställt in det.\n\nVem i ditt lag skulle betala mest? Tagga hen. 👇","hash":HASH_MAIN+" #lagkassan #böter"},
 {"id":"03-badges","slides":[hero("Vem blir<br><span>Klubblegend</span><br>i ditt lag?","Samla badges, rösta fram matchens lirare och skapa lagkänsla efter varje match.",[("👑","Klubblegend","100 matcher"),("🎯","Skyttekung","50 mål"),("🤝","Passningskungen","25 assist"),("⏰","Lagets Försenade","Alla vet vem det är")])],
  "caption":"Vem i laget kommer först till Klubblegend? 👑\n\nI SquadGame finns över 90 badges att samla, från Skyttekung till Lagets Försenade. Vilken badge vill du ha mest?\n\nBerätta i kommentarerna. 👇","hash":HASH_MAIN+" #badges"},
 {"id":"04-pilotlag","slides":[hero("Söker <span>pilotlag</span>.<br>Är ditt lag med?","Vi bygger SquadGame tillsammans med riktiga lag. Gratis att testa, och ni får vara med och påverka.",[("💬","Lagchatt","en plats för laget"),("📸","Galleri","säsongens minnen"),("⭐","Matchens lirare","röstas fram av laget"),("🎖️","Badges","att samla hela säsongen")],right="DM:a oss →")],
  "caption":"Vi söker lag som vill testa SquadGame. ⚽\n\nOm du är tränare, lagledare eller spelare och vill ha mer lagkänsla efter match och träning: skicka ett DM så fixar vi det.\n\nTagga en lagledare som borde se det här. 👇","hash":HASH_MAIN+" #lagledare #fotbollstränare"},
 {"id":"05-allt-pa-ett-stalle","slides":[hero("Där laget bor<br><span>mellan matcherna</span>","Slipp en död gruppchatt, borttappade bilder och sena besked. Allt laget behöver finns på ett ställe.",[("💬","Lagchatt","skämt och logistik"),("📸","Säsongsgalleri","bilder från hela året"),("🗳️","Omröstningar","laget bestämmer"),("📅","Spelschema","hemma, borta, resultat")])],
  "caption":"Gruppchatten dör, bilderna försvinner och ingen vet när matchen är. 🙃\n\nSquadGame samlar chatt, galleri, omröstningar och spelschema för ditt lag på ett ställe.\n\nVad saknar ni mest i er gruppchatt? 👇","hash":HASH_MAIN+" #gruppchatt"},
 {"id":"06-karusell-lagkansla","slides":None,
  "caption":"5 enkla sätt att få mer lagkänsla, utan att det kostar något. ⚽\n\nSpara inlägget och skicka det till din lagledare. Vilket tips har ni testat? 👇","hash":HASH_MAIN+" #lagbygge #träning"},
]
TIPS = [("Rösta fram matchens lirare","Efter varje match. Det tar en minut och ger ett samtal i omklädningsrummet som håller i flera dagar."),
        ("Samla bilderna på ett ställe","Ett gemensamt galleri för säsongen. Slipp leta i fem olika chattar efter bilden från cupen."),
        ("Ha en rolig bötesregel","Försent, glömd utrustning eller hemsk tackling. Lagkassan blir till cupresa eller avslutning."),
        ("Låt laget bestämma","Tröjfärg, avslutningsmiddag eller veckans övning. En snabb omröstning ger alla en röst.")]
POSTS[5]["slides"] = [cover("5 sätt att få <span>mer lagkänsla</span>","Enkla grepp som fungerar för alla lag, oavsett nivå.")] + [tip(i+1,t,b,5) for i,(t,b) in enumerate(TIPS)] + [outro()]
# karusellen har 6 sidor: omslag + 4 tips + avslut (tips-räknaren visar x / 5 -> justera till 4)
for i in range(1,5):
    POSTS[5]["slides"][i] = tip(i, TIPS[i-1][0], TIPS[i-1][1], 4)

POSTS += [
 {"id":"07-skytteliga","slides":[phone("Vem blir<br><span>skyttekung</span> i år?","Följ skytteligan, assistligan och poängligan i appen. Alla ser tabellen, alla vill upp på pallen.","app-league.jpg")],
  "caption":"Skyttekung, assistkung eller poängkung? 🥇\n\nI SquadGame finns ligatabeller för mål, assist, poäng och matchens lirare under hela säsongen. Då blir även en vanlig träningsvecka en tävling.\n\nVem i ditt lag leder skytteligan just nu? 👇","hash":HASH_MAIN+" #skytteliga"},
 {"id":"08-boter-app","slides":[phone("Lagkassan<br><span>under kontroll</span>","Dela ut böter enligt lagets egna regler och håll koll på vad som är betalt. Swish fungerar om laget har ställt in det.","app-fines.jpg")],
  "caption":"Gult kort för snack, mobil under genomgång eller bara försent. 😄\n\nI SquadGame sköter ni böterna i appen. Ni ser vad som är obetalt och hur mycket som ligger i lagkassan.\n\nVilken är den konstigaste bötesregeln ni har? 👇","hash":HASH_MAIN+" #lagkassan"},
 {"id":"09-veckans-vinnare","slides":[phone("Veckans <span>vinnare</span><br>firas i appen","Ladda upp en bild på veckans träningsvinnare och dela den direkt på Instagram. Laget får sitt ögonblick.","app-dashboard.jpg")],
  "caption":"Träningsvinnarna förtjänar också en bild. 🏆\n\nI SquadGame laddar ni upp veckans vinnare och delar den på Instagram med några tryck.\n\nVem i laget skulle vinna varje vecka om det gick? 👇","hash":HASH_MAIN+" #träningsvinnare"},
]

def main():
    md = ["# SquadGame – captions\n"]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME) if os.path.exists(CHROME) else p.chromium.launch()
        pg = b.new_page(viewport={'width':1080,'height':1350})
        for post in POSTS:
            files = []
            for n, s in enumerate(post["slides"], 1):
                tmp = os.path.join(HERE, "_tmp.html"); open(tmp,"w",encoding="utf-8").write(s)
                pg.goto("file://"+tmp); pg.wait_for_timeout(300)
                name = f'{post["id"]}.png' if len(post["slides"])==1 else f'{post["id"]}-{n}.png'
                pg.screenshot(path=os.path.join(OUT,name)); files.append(name)
            md.append(f'## {post["id"]}\nBilder: {", ".join(files)}\n\n{post["caption"]}\n\n{post["hash"]}\n')
        b.close()
    os.remove(os.path.join(HERE,"_tmp.html"))
    open(os.path.join(HERE,"captions.md"),"w",encoding="utf-8").write("\n".join(md))
    print("klart:", len(os.listdir(OUT)), "bilder")
main()
