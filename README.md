# Corvinus szd.lib scraper  

## Leírás
A python script végigjárja a http://szd.lib.uni-corvinus.hu/ alatt található számmal jelölt oldalakat.   
Összeállít egy listát a html kód meta-tag-el jelölt részeiből, ezután megpróbálja letölteni a beágyazott pdf documentumot.  
Ha titkosítva lett a szakdolgozat, akkor a html 404-et fog adni, ezeket a tételeket ignorálja a script.  
Ha több dokumentum van (eprints.document_url), (pl vannak a szakdolgozaton kívül mellékletek is), akkor azokat is letölti.  
A fileok elnevezése az eprints.eprintid alapján történik,  
pl http://szd.lib.uni-corvinus.hu/2337 oldal alatt található dokumentumot 2337.pdf-nek nevezi el, ha több dokumentumot talál, akkor 2337_1.pdf, 2337_2.pdf stb.  
Az első letöltés után létrehoz egy szd_lib_info_table_{time_stamp}.xlsx reportot.  
Ezt a status reportot minden letöltésnél újraírja, így ha bármilyen okból megszakadna a letöltés, akkor is pontosan tudjuk, hogy eddig mit nézett át.  
Ezután a kezdeti paramétert módosítva kényelmesen folytathatjuk a letöltést.  
A szd_lib_info_table_{time_stamp}.xlsx tartalmazza a meta tagekben megtalálható összes információt, nagyon hasznos lehet további elemzésekhez.  
Tartalmazza az eprints.id-t is ami ugyananaz mint egy adott file elnevezése.  

## Paraméterek:  
Jelenleg meg kell nyitni a filet a paraméterek beállításához.   
    from_id: első oldal, ahonnan letölteni szeretnénk  
    to_id:  az utolsó letölteni kívánt oldal  
    out_dir: itt adhatjuk meg, hogy hová töltsön le pl r"C:\Users\user\Downloads"  
    wait_s: két lekérdezés között a script mindig vár 'wait_s' másodpercnyi időt  
    spoof: default False, ha True, akkor referebe beírja, hogy a http://szd.lib.uni-corvinus.hu/cgi/search/advanced oldalról lett átirányítva illetve generál egy random user-agentet.   
    Persze az IP cím így is azonos marad az összes lekérdezésnél.
    download: itt megadhatjuk hogy letöltse-e a pdf-eket a script, default letölt.  

## Installok  
Python verzió: python3.*  
ha van fönn standard python installáció, akkor ezeket a modulokat kell telepíteni:  
pandas, requests, beautifulsoup4, user_agent, openpyxl  
megosztott gépen ajánlom a user flag használatát:  
    pip install pandas --user  
    pip install requests --user  
    pip install beautifulsoup4 --user  
    pip install user_agent --user  
    pip install openpyxl --user  
    
## TODO
requirements.txt