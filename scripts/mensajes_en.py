"""Lo que dicen los scripts, en ingles, para una vitrina con "language": "en".

La clave es el texto en castellano tal como esta en el codigo, dentro de
`_()`; el valor, su traduccion, con los mismos huecos `{...}`. Una prueba
(Traducciones, en pruebas.py) comprueba que no falta ninguno y que los huecos
coinciden, asi que un mensaje nuevo sin traducir para el CI.
"""

MENSAJES = {
    # --- al-dia.py ---------------------------------------------------------------
    "cuelga cada ficha de su sección": "links each entry to its room",
    "apunta la fecha de alta que falte": "records any missing date added",
    "convierte en opinión lo que hayas escrito suelto": "turns what you wrote loose into its opinion",
    "baja las carátulas que falten": "downloads missing covers",
    "rellena año, autor y tags": "fills in year, author and tags",
    "escribe el «De qué va»": "writes the “What it's about”",
    "escribe las páginas de autor": "writes the author pages",
    "solo una carpeta": "only one folder",
    "salta portadas, datos y textos": "skips covers, data and texts",
    "no escribe nada": "doesn't write anything",
    "Al día. Lo que falta rellenar a mano: scripts/estado.py --detalle":
        "Up to date. What's left to fill in by hand: scripts/estado.py --detail",
    "Han fallado: {scripts}. El resto ha terminado.": "These failed: {scripts}. The rest finished.",

    # --- autores.py --------------------------------------------------------------
    "obras que hacen falta para tener pagina (por defecto 2)": "works needed to get a page (default 2)",
    "borra las paginas de autor": "deletes the author pages",
    "{n} páginas de autor": "{n} author pages",
    "{n} autores con menos de {minimo} obras se quedan en texto, sin página.":
        "{n} authors with fewer than {minimo} works stay as plain text, without a page.",
    "{fichas} fichas, {paginas} paginas de autor": "{fichas} entries, {paginas} author pages",
    ", {n} fichas limpiadas de enlaces viejos.": ", {n} entries cleaned of old links.",

    # --- datos.py, textos.py, portadas.py -------------------------------------------
    "la ficha no tiene appid; se pone a mano": "the entry has no appid; add it by hand",
    "la ficha no tiene tvmaze; se pone a mano": "the entry has no tvmaze; add it by hand",
    "la ficha no tiene mbid; se pone a mano": "the entry has no mbid; add it by hand",
    "la ficha no tiene coverid; se pone a mano": "the entry has no coverid; add it by hand",
    "fichas sueltas; por defecto, todas": "single entries; by default, all of them",
    "reescribe los campos que ya tienen valor": "rewrites fields that already have a value",
    "no consulta ni escribe nada": "doesn't query or write anything",
    "MusicBrainz no tiene generos votados de {id} ni de su artista":
        "MusicBrainz has no voted genres for {id} or its artist",
    "la tienda no tiene ficha del appid {id}": "the store has no page for appid {id}",
    "TVmaze no responde por el id {id}": "TVmaze doesn't answer for id {id}",
    "TVmaze no tiene ficha del id {id}": "TVmaze has no page for id {id}",
    "su ficha de TVmaze esta vacia ({id})": "its TVmaze page is empty ({id})",
    "MusicBrainz no responde por el mbid {id}": "MusicBrainz doesn't answer for mbid {id}",
    "Open Library no responde por el coverid {id}": "Open Library doesn't answer for coverid {id}",
    "Open Library no encuentra la obra del coverid {id}": "Open Library can't find the work for coverid {id}",
    "{hechas} fichas completadas, {fallidas} sin resolver, {saltadas} ya estaban.":
        "{hechas} entries completed, {fallidas} unresolved, {saltadas} already done.",
    "MusicBrainz (los de {nombre}: el disco no tiene)": "MusicBrainz ({nombre}'s: the album has none)",
    "no hay fuente para '{tipo}'; se rellena a mano": "there's no source for '{tipo}'; fill it in by hand",
    "buscaría {campos}": "would look for {campos}",
    "reescribe el cuerpo de las fichas que ya tienen texto": "rewrites the body of entries that already have text",
    "el articulo «{articulo}» no trae resumen": "the article “{articulo}” has no summary",
    "su ficha de Steam no trae descripcion ({id})": "its Steam page has no description ({id})",
    "ni articulo en Wikipedia ({wiki}) ni sinopsis en Letterboxd ({id})":
        "no Wikipedia ({wiki}) article and no Letterboxd synopsis ({id})",
    "ni articulo en Wikipedia ({wiki}) ni resumen en TVmaze ({id})":
        "no Wikipedia ({wiki}) article and no TVmaze summary ({id})",
    "Wikidata no enlaza este libro con la Wikipedia ({wiki}); pon el campo `wikipedia` a mano":
        "Wikidata doesn't link this book to Wikipedia ({wiki}); set the `wikipedia` field by hand",
    "MusicBrainz no da la lista de canciones ({id})": "MusicBrainz doesn't give the track list ({id})",
    "buscaría su texto": "would look for its text",
    "{hechas} fichas escritas, {fallidas} sin resolver, {saltadas} ya tenian texto.":
        "{hechas} entries written, {fallidas} unresolved, {saltadas} already had text.",
    "no hay fuente para '{tipo}'": "there's no source for '{tipo}'",
    "rehace las que ya tienen portada": "redoes the ones that already have a cover",
    "no baja ni escribe nada": "doesn't download or write anything",
    "Steam (exacta, por appid)": "Steam (exact, by appid)",
    "Open Library (exacta, por coverid)": "Open Library (exact, by coverid)",
    "sin portada en la fuente": "no cover at the source",
    "{hechas} portadas nuevas, {fallidas} sin resolver, {saltadas} ya la tenian.":
        "{hechas} new covers, {fallidas} unresolved, {saltadas} already had one.",
    "Wikipedia ({articulo}), en baja resolucion": "Wikipedia ({articulo}), low resolution",
    "sin id de Letterboxd: {porque}": "no Letterboxd id: {porque}",
    "Cover Art Archive (exacta, por mbid de {clase})": "Cover Art Archive (exact, by {clase} mbid)",
    "tipo '{tipo}' desconocido": "unknown type '{tipo}'",
    "buscaria en {fuente}": "would search {fuente}",

    # --- desde_issue.py -----------------------------------------------------------
    "el enlace tiene que ser una dirección web (https://...)": "the link has to be a web address (https://...)",
    "falta el JSON del evento": "the event JSON is missing",
    "la fecha «{fecha}» no es AAAA, AAAA-MM ni AAAA-MM-DD": "the date “{fecha}” isn't YYYY, YYYY-MM or YYYY-MM-DD",
    "Ya estaba en la vitrina ({ruta}); no he tocado nada.": "It was already on display ({ruta}); nothing touched.",
    "la nota tiene que ir del 1 al 10, no «{nota}»": "the rating has to be from 1 to 10, not “{nota}”",
    "el estado «{estado}» no es ninguno de {estados}": "the status “{estado}” isn't any of {estados}",
    "el grupo «{grupo}» lleva caracteres que no valen": "the group “{grupo}” has characters that aren't allowed",
    "No he añadido nada: {porque}.": "Nothing added: {porque}.",
    "No he podido añadirla. Lo último que dijo nueva.py:": "Couldn't add it. The last thing nueva.py said:",
    "Añadida: `{ruta}`.": "Added: `{ruta}`.",
    "La frase va como tu opinión, en «{titulo}».": "The sentence goes in as your opinion, under “{titulo}”.",
    "Prueba sin escribir nada:": "Dry run, nothing written:",

    # --- enmarcar.py, fechas.py, secciones.py -------------------------------------------
    "Convierte en opinión lo que hayas escrito suelto en una ficha.":
        "Turns what you wrote loose in an entry into its opinion.",
    "Apunta en cada ficha cuando entro en la coleccion: el campo `added`.":
        "Records in each entry when it joined the collection: the `added` field.",
    "Cuelga cada ficha de su seccion: escribe el campo `section`.":
        "Links each entry to its room: writes the `section` field.",
    "{n} fichas por enmarcar.": "{n} entries to frame.",
    "{n} fichas enmarcadas.": "{n} entries framed.",
    "{n} fichas sin fecha.": "{n} entries without a date.",
    "{n} fichas fechadas.": "{n} entries dated.",
    "quita el campo": "removes the field",
    "quitaria el campo en {n} fichas": "would remove the field from {n} entries",
    "escribiria el campo en {n} fichas": "would write the field in {n} entries",
    "{n} fichas sin campo": "{n} entries without the field",
    "{n} fichas colgadas": "{n} entries linked",

    # --- estado.py --------------------------------------------------------------------
    "FICHAS": "ENTRIES",
    "SIN RELLENAR": "MISSING",
    "FAVORITOS": "FAVORITES",
    "ESTADOS": "STATUSES",
    "NOTAS": "RATINGS",
    "PORTADAS": "COVERS",
    "EN LA WEB": "ON THE SITE",
    "total": "total",
    "borrador": "draft",
    "publicadas": "published",
    "con texto": "with text",
    "texto": "text",
    "sin poner": "unset",
    "{n} de {total}": "{n} of {total}",
    "lista las fichas a las que les falta algo": "lists the entries that are missing something",
    "avisa de lo que se ha quedado atras, sin tocar nada": "warns about what's fallen behind, without touching anything",
    "Nada atrasado.": "Nothing behind.",
    "No hay ninguna ficha todavía.": "There are no entries yet.",
    "  Ninguna. La web se salta lo que lleva `draft: true`; en Obsidian se\n  ven todas. Para ascender una, quítale esa línea.":
        "  None. The site skips anything with `draft: true`; Obsidian shows\n  them all. To publish one, remove that line.",
    "  Ninguna. Favoritos.base y las vistas «Solo favoritos» salen vacías\n  hasta que alguna ficha lleve `favorite: true`.":
        "  None. Favoritos.base and the favorites views stay empty\n  until some entry has `favorite: true`.",
    "Pasa scripts/fechas.py": "Run scripts/fechas.py",
    "Nada. Están todas completas.": "Nothing. They're all complete.",
    "  {n} ficha(s) sin estado: no salen ni en la vista de lo\n  terminado ni en la lista de lo que queda.":
        "  {n} entr(ies) without a status: they show up neither among the\n  finished nor in the list of what's left.",
    "  {n} ficha(s) con un estado que no existe, que es\n  la otra manera de no salir en ninguna de las dos:":
        "  {n} entr(ies) with a status that doesn't exist, which is\n  the other way of showing up in neither:",
    "{n} portada(s) que ya no usa ninguna ficha: ": "{n} cover(s) no entry uses any more: ",
    "{n} ficha(s) apuntan a una imagen que no está:": "{n} entr(ies) point to an image that isn't there:",
    "{n} imagen(es) que ya no usa ninguna ficha:": "{n} image(s) no entry uses any more:",
    "{n} ficha(s) sin fecha de alta, que no saldran en Recien llegadas: ":
        "{n} entr(ies) without a date added, which won't show in Just arrived: ",
    "… y {n} más (--detalle las lista)": "… and {n} more (--detail lists them)",

    # --- importar.py -------------------------------------------------------------------
    "{n} ficha(s) se crearían en {carpeta}, {ya} ya estaba(n).":
        "{n} entr(ies) would be created in {carpeta}, {ya} already there.",
    "{n} ficha(s) creada(s) en {carpeta}, {ya} ya estaba(n).":
        "{n} entr(ies) created in {carpeta}, {ya} already there.",
    "No he encontrado ningún csv de Letterboxd en esa ruta.": "No Letterboxd csv found at that path.",
    "El diario no tiene entradas de películas.": "The diary has no film entries.",
    "No he encontrado juegos en esa ruta. Lo que entiende:\n  - steamcommunity.com/my/games?tab=all guardada con Ctrl+S,\n    con la sesión abierta\n  - el zip del export de datos de Steam":
        "No games found at that path. What it understands:\n  - steamcommunity.com/my/games?tab=all saved with Ctrl+S,\n    while logged in\n  - the zip of the Steam data export",
    "No he encontrado datos de Spotify en esa ruta.": "No Spotify data found at that path.",
    "hora": "hour",
    "horas": "hours",
    "minuto": "minute",
    "minutos": "minutes",
    "Ahora: scripts/al-dia.py": "Next: scripts/al-dia.py",
    "dice qué haría, sin escribir": "says what it would do, without writing",
    "sin umbrales: entra todo lo que traiga el export": "no thresholds: everything in the export comes in",
    "las fichas entran publicadas, sin draft": "entries come in published, without draft",
    "export de Letterboxd": "Letterboxd export",
    "el .zip del export, la carpeta o un csv suelto": "the export .zip, the folder or a single csv",
    "el diario público, sin cuenta Pro": "the public diary, no Pro account needed",
    "tu nombre de usuario en Letterboxd": "your Letterboxd username",
    "lo que tienes por ver, sin cuenta Pro": "your watchlist, no Pro account needed",
    "export de datos de Steam": "Steam data export",
    "el .zip del export o la carpeta": "the export .zip or the folder",
    "lo más escuchado, sin clave ninguna": "most listened, no key needed",
    "tu nombre de usuario en listenbrainz.org": "your listenbrainz.org username",
    "ventana (por defecto, año)": "time window (default: year)",
    "cuántos discos (por defecto 40)": "how many albums (default 40)",
    "busca un libro en Open Library y crea la ficha": "finds a book in Open Library and creates the entry",
    "el título, o título y autor": "the title, or title and author",
    "quédate con el resultado N sin preguntar": "take result N without asking",
    "cuántos resultados enseñar (por defecto 5)": "how many results to show (default 5)",
    "ponle ya la nota, del 1 al 10": "give it a rating now, from 1 to 10",
    "por defecto, pendiente": "pending by default",
    "lo mismo desde el zip, sin crear app": "the same from the zip, no app needed",
    "el .zip del export de Spotify o la carpeta": "the Spotify export .zip or the folder",
    "pliega tus canciones guardadas en los discos que las llevan": "folds your saved tracks into the albums they're on",
    "Leído: {que}": "Read: {que}",
    "Diario de {usuario}: {n} películas.": "{usuario}'s diary: {n} films.",
    "Leída la watchlist de {usuario}: {cuantas}.": "Read {usuario}'s watchlist: {cuantas}.",
    "{cuantos} entre lo más escuchado {cuando}.": "{cuantos} among the most listened {cuando}.",
    "del último mes": "in the last month",
    "del último trimestre": "in the last quarter",
    "del último medio año": "in the last half year",
    "del último año": "in the last year",
    "de siempre": "of all time",
    "No he encontrado canciones guardadas en esa ruta. Van en la\nclave tracks de YourLibrary.json, que trae el export de la cuenta.":
        "No saved tracks found at that path. They're under the\ntracks key of YourLibrary.json, in the account export.",
    "No hay YourLibrary.json en esa ruta, que es donde va lo guardado.":
        "There's no YourLibrary.json at that path, which is where saved items go.",
    "Sin historial con álbum no puedo ordenar por lo más escuchado.\nCon --completo entran los álbumes guardados que traiga el export.":
        "Without a history that has albums I can't sort by most listened.\nWith --all, the saved albums in the export come in.",
    "{n} disco(s) entre lo más escuchado ({tiempo} en total).": "{n} album(s) among the most listened ({tiempo} in total).",
    "Se parecen a fichas que ya tenías. Si son la misma obra, únelas:":
        "These look like entries you already had. If they're the same work, merge them:",
    "Entran con draft: true, así que no salen en la web hasta que les\nquites la línea. En Obsidian se ven todas.":
        "They come in with draft: true, so they won't show on the site until\nyou remove that line. Obsidian shows them all.",
    "No he podido leer el diario de '{usuario}'. Comprueba el nombre y\nque el perfil no sea privado.":
        "Couldn't read '{usuario}''s diary. Check the name and\nthat the profile isn't private.",
    "La watchlist de '{usuario}' está vacía o no es pública.": "'{usuario}''s watchlist is empty or not public.",
    "película": "film",
    "películas": "films",
    "No he podido leer las estadísticas de '{usuario}'. Comprueba el\nnombre de usuario en listenbrainz.org.":
        "Couldn't read '{usuario}''s stats. Check the\nusername on listenbrainz.org.",
    "'{usuario}' no tiene escuchas registradas en esa ventana.\nSi acabas de crear la cuenta, conecta Spotify o sube tu historial\nampliado en listenbrainz.org/settings/import y vuelve luego.":
        "'{usuario}' has no listens recorded in that window.\nIf you just created the account, connect Spotify or upload your extended\nhistory at listenbrainz.org/settings/import and come back later.",
    "disco": "album",
    "discos": "albums",
    "{n} reproducción(es) sin nombre de álbum. Eso es el historial\ncorto del export de la cuenta, que no lo trae: para ordenar por lo más\nescuchado hace falta pedir el historial ampliado, que tarda hasta un mes.":
        "{n} play(s) without an album name. That's the short history\nof the account export, which doesn't include it: to sort by most\nlistened you need to request the extended history, which takes up to a month.",
    "{canciones} guardadas en {discos}.": "{canciones} saved across {discos}.",
    "{n} disco(s) con {minimo} o más entran como favoritos.": "{n} album(s) with {minimo} or more come in as favorites.",
    "{n} álbum(es) guardado(s).": "{n} saved album(s).",
    "menos de {n} horas": "less than {n} hours",
    "{n} ficha(s) apartada(s) por el modo rápido ({umbral}). Con --completo entran todas.":
        "{n} entr(ies) left out by quick mode ({umbral}). With --all they all come in.",
    "juegos: horas mínimas jugadas (por defecto {n})": "games: minimum hours played (default {n})",
    "discos: canciones tuyas mínimas (por defecto {n})": "albums: minimum saved tracks (default {n})",
    "películas: nota mínima (por defecto {n}, o sea 4 estrellas)": "films: minimum rating (default {n}, i.e. 4 stars)",
    "canción": "track",
    "canciones": "tracks",
    "menos de {n} canciones tuyas": "fewer than {n} of your tracks",
    "nota por debajo de {n}, o ninguna": "rating below {n}, or none",
    "No he podido leer la watchlist de '{usuario}'. Comprueba el\nnombre y que el perfil no sea privado.":
        "Couldn't read '{usuario}''s watchlist. Check the\nname and that the profile isn't private.",

    # --- nueva.py ------------------------------------------------------------------
    "animación": "animation",
    "documental": "documentary",
    "Wikidata la conoce, pero sin id de Steam, Letterboxd, TVmaze, Open Library ni MusicBrainz":
        "Wikidata knows it, but without a Steam, Letterboxd, TVmaze, Open Library or MusicBrainz id",
    "Wikidata no contesta ahora mismo; inténtalo dentro de un rato": "Wikidata isn't answering right now; try again in a while",
    "Wikidata no tiene esa obra enlazada": "Wikidata doesn't have that work linked",
    "sin estrenar": "unreleased",
    "su ficha de Letterboxd no dice quien dirige": "its Letterboxd page doesn't say who directed it",
    "tiene que ser AAAA, AAAA-MM o AAAA-MM-DD": "it has to be YYYY, YYYY-MM or YYYY-MM-DD",
    "tipo|enlace": "type|link",
    "titulo": "title",
    "lo que escribirias en un buscador": "what you'd type into a search box",
    "sin preguntar: el resultado numero N": "without asking: result number N",
    "NOMBRE": "NAME",
    "como se llama el fichero, si del titulo no sale uno": "the file name, if the title doesn't give one",
    "entra con draft: true, o sea sin salir en la web": "comes in with draft: true, i.e. not on the site",
    "entra con hidden: true: no sale en la web, pero esta en el repo":
        "comes in with hidden: true: not on the site, but it is in the repo",
    "va a la carpeta privada, que no se sube a ningun sitio": "goes into the private folder, which is never uploaded",
    "la mete en ese grupo; se puede repetir": "puts it in that group; can be repeated",
    "AAAA[-MM[-DD]]": "YYYY[-MM[-DD]]",
    "cuando la terminaste, para el anuario": "when you finished it, for the yearbook",
    "no escribe ni baja nada": "doesn't write or download anything",
    "Entra con draft: true, así que no sale en la web hasta que le quites\nla línea. En Obsidian se ve ya.":
        "It comes in with draft: true, so it won't show on the site until you\nremove that line. Obsidian already shows it.",
    "Sin nota: ponla con scripts/repasar.py o en Obsidian cuando la\ntengas, que es por lo que ordenan las galerías.":
        "No rating: add it with scripts/repasar.py or in Obsidian when you\nhave one, it's what the galleries sort by.",
    "(sin portada)": "(no cover)",
    "Wikidata no enlaza esa obra con la fuente de {carpeta}": "Wikidata doesn't link that work to the source for {carpeta}",
    "Prueba con el título en inglés: el catálogo va casi todo por ahí.":
        "Try the English title: the catalogue is mostly in English.",
    "Prueba con el título original: es el que suele estar en Wikidata.":
        "Try the original title: it's usually the one in Wikidata.",
    "portada: {detalle}": "cover: {detalle}",
    "texto: {detalle}": "text: {detalle}",
    "{porque} (enlace de {sitio})": "{porque} ({sitio} link)",
    "{tipos}, o el enlace de la obra": "{tipos}, or the link to the work",
    "falta qué buscar": "nothing to search for",
    "No he podido hablar con {fuente}. No es que no esté:\nes que ahora mismo no contesta. Inténtalo dentro de un rato.":
        "Couldn't reach {fuente}. It's not that it isn't there:\nit isn't answering right now. Try again in a while.",
    "{fuente} no tiene nada en ese enlace. Prueba a buscarla por el título:\n  scripts/nueva.py {tipo} \"el título\"":
        "{fuente} has nothing at that link. Try searching by title:\n  scripts/nueva.py {tipo} \"the title\"",
    "No encuentro nada con «{titulo}».": "Nothing found for “{titulo}”.",
    "El título de verdad se guarda igual, en `title`.": "The real title is still kept, in `title`.",
    "Creada {ruta}": "Created {ruta}",
    "no la he encontrado; se pone a mano": "not found; add it by hand",
    "ese enlace no es de ningún sitio que sepa leer. Los que sí: {sitios}":
        "that link isn't from any site I can read. These are: {sitios}",
    "ese enlace es de {suyo}, no de {pedido}": "that link is for {suyo}, not {pedido}",
    "el tipo es uno de estos: {tipos}; o un enlace": "the type is one of: {tipos}; or a link",
    "Sin terminal para preguntar. Repite con --elegir N.": "No terminal to ask in. Run it again with --pick N.",
    "No se ha creado nada.": "Nothing was created.",
    "Esa ya la tienes: {ruta} lleva el mismo id.": "You already have it: {ruta} has the same id.",
    "El título no da un nombre de fichero; {fuente} lo llama «{nombre}».":
        "The title doesn't give a file name; {fuente} calls it “{nombre}”.",
    "Se crearía {ruta}": "Would create {ruta}",
    "«{titulo}» ya estaba en {carpeta}.": "“{titulo}” was already in {carpeta}.",
    "Se parece a una que ya tenías: {aviso}": "Looks like one you already had: {aviso}",
    "Búscala por el título: scripts/nueva.py {tipo} \"el título\"": "Search for it by title: scripts/nueva.py {tipo} \"the title\"",
    "Solo hay {n} resultados.": "There are only {n} results.",
    "sin texto ({porque})": "no text ({porque})",
    "«{titulo}» no tiene ni una letra latina, y {fuente} no sabe cómo se llama fuera\nde su alfabeto, así que de ahí no sale un nombre de fichero.\nDilo tú, repitiendo la orden con --fichero y el nombre que le des:":
        "“{titulo}” has no Latin letters at all, and {fuente} doesn't know its name outside\nits alphabet, so no file name comes out of it.\nGive one yourself by repeating the command with --file and the name:",

    "Escritas las plantillas de {carpeta}.": "Wrote the templates in {carpeta}.",

    # --- repasar.py -----------------------------------------------------------------
    "escrito": "written",
    "tambien las que ya tienen nota y estado": "also the ones that already have a rating and status",
    "Esto pregunta ficha a ficha, y hace falta una terminal para contestar.":
        "This asks entry by entry, and needs a terminal to answer in.",
    "No hay ninguna sin nota ni estado.": "There are none without a rating or status.",
    "{tocadas} ficha(s) cambiadas, {frases} con frase nueva.": "{tocadas} entr(ies) changed, {frases} with a new sentence.",
    "nota {nota} · {estado}": "rating {nota} · {estado}",
    "{n} fichas por repasar.": "{n} entries to go through.",
    "por qué está en la vitrina (Enter para saltar): ": "why it's on display (Enter to skip): ",
    "la nota va del 1 al 10, no {nota}": "the rating goes from 1 to 10, not {nota}",
    "no entiendo «{trozo}»": "I don't understand “{trozo}”",
    "{error}. Otra vez, o ? para la ayuda.": "{error}. Try again, or ? for help.",

    # --- vistazo.py, vitrina.py ----------------------------------------------------------
    "construye en web/vistazo/ y no levanta nada": "builds into web/vistazo/ and doesn't serve it",
    "Falta instalar la web: cd web && npm ci --ignore-scripts --include=optional":
        "The site isn't installed yet: cd web && npm ci --ignore-scripts --include=optional",
    "puerto del servidor (por defecto {n})": "server port (default {n})",
    "El vistazo está en {url}  (Ctrl+C para salir)": "The preview is at {url}  (Ctrl+C to quit)",
    "no he podido consultar Wikidata": "couldn't query Wikidata",
    "Wikidata no la encuentra": "Wikidata can't find it",
    "varias del mismo año y ninguna encaja mejor": "several from the same year and none fits better",
    "ya estaba en la ficha": "already in the entry",
    "Eso no es una de las opciones.": "That isn't one of the options.",
    "{n} candidatas y la ficha no dice el año": "{n} candidates and the entry doesn't say the year",
    "ninguna es de {year}: ": "none is from {year}: ",
    "¿Cuál? (1-{n}, Enter para el 1, 0 si ninguno): ": "Which one? (1-{n}, Enter for 1, 0 for none): ",
    "cuantas veces la has terminado: vista, jugada, leida o escuchada": "how many times you've finished it: watched, played, read or listened to",
    "une cada ficha con Wikidata: de qué otra viene": "links each entry with Wikidata: which other it comes from",
    "las fichas que mirar; sin nada, todas": "the entries to look at; with none, all of them",
    "dice que pondria, sin tocar nada": "says what it would write, without touching anything",
    "Preguntando a Wikidata por {n} fichas…": "Asking Wikidata about {n} entries…",
    "{n} fichas con algo nuevo; {m} sin elemento en Wikidata.": "{n} entries with something new; {m} without a Wikidata item.",
    # desde_issue.py, editar
    'la opinión': 'the opinion',
    '«{ficha}» no es una ficha de la vitrina': '“{ficha}” is not an entry on display',
    'la opinión, quitada': 'the opinion, removed',
    '`{ruta}` ya estaba así; no he tocado nada.': "`{ruta}` was already like that; I didn't touch anything.",
    'Cambiado en `{ruta}`:': 'Changed in `{ruta}`:',
    'No he cambiado nada: {porque}.': "I didn't change anything: {porque}.",
    # cuando.py
    'No he encontrado diary.csv en esa ruta.': "I couldn't find diary.csv at that path.",
    'Diario de Letterboxd (export): {n} entradas.': 'Letterboxd diary (export): {n} entries.',
    'Diario de Letterboxd de {usuario}: {n} entradas.': "{usuario}'s Letterboxd diary: {n} entries.",
    'Logros de Steam: {n} juegos por mirar.': 'Steam achievements: {n} games to check.',
    'Los logros de ese perfil son privados. En Steam: Editar perfil →\nPrivacidad → Detalles de juegos, en Público.': "That profile's achievements are private. On Steam: Edit profile →\nPrivacy → Game details, set to Public.",
    'De Goodreads hace falta el número de usuario: el de goodreads.com/user/show/NÚMERO.': 'Goodreads needs the user number: the one in goodreads.com/user/show/NUMBER.',
    'Goodreads no ha devuelto ningún libro con fecha de leído. Comprueba el\nnúmero y que la estantería sea pública.': 'Goodreads returned no book with a read date. Check the number\nand that the shelf is public.',
    'Goodreads: {n} libros con fecha de leído.': 'Goodreads: {n} books with a read date.',
    "ListenBrainz no tiene escuchas de '{usuario}'.": "ListenBrainz has no listens for '{usuario}'.",
    'ListenBrainz: {n} escuchas.': 'ListenBrainz: {n} listens.',
    'No he encontrado el historial ampliado de Spotify en esa ruta\n(Streaming_History_Audio_*.json). El export normal no trae los discos.': "I couldn't find Spotify's extended history at that path\n(Streaming_History_Audio_*.json). The regular export has no albums.",
    'Spotify: {n} escuchas.': 'Spotify: {n} listens.',
    'de dónde; sin nada, las de la config': 'where from; with nothing, the ones in the config',
    'usuario, perfil o ruta del export': 'user, profile or path to the export',
    'Sin cuentas en vitrine.local.json: nada que mirar.': 'No accounts in vitrine.local.json: nothing to check.',
    'No sé de dónde sacarlo: pon la cuenta detrás (scripts/cuando.py\nletterboxd TU_USUARIO) o déjala en vitrine.local.json.': "I don't know where to get it from: put the account after it (scripts/cuando.py\nletterboxd YOUR_USER) or leave it in vitrine.local.json.",
    '{n} ficha(s) cambiarían.': '{n} entry(ies) would change.',
    '{n} ficha(s) cambiada(s).': '{n} entry(ies) changed.',
    'apunta cuándo terminaste o empezaste cada cosa': 'notes when you finished or started each thing',
}

# La guia de repasar.py, entera.
MENSAJES["""\
Cómo contestar, en una línea y en cualquier orden:

  NOTA       1 … 10      la nota
  ESTADO     p           pendiente
             c           en curso
             t           terminado
             a           abandonado
  FAVORITA   f  / -f     favorita / deja de serlo

  Enter      la deja como está y pasa a la siguiente
  ?          enseña otra vez esta guía
  q          para aquí; lo contestado ya está guardado

  Ejemplos:  9 f     → nota 9, favorita y terminado
             7 a     → nota 7 y abandonado
             c       → en curso, sin nota todavía
  Con nota y sin estado se entiende terminado, salvo que ya dijera en curso
  o abandonado.

  Después, si la ficha no tiene nada tuyo escrito, te pide por qué está en
  la vitrina: lo que te dejó, bueno o malo. Va arriba del todo en la ficha,
  como tu opinión. Enter la salta.
"""] = """\
How to answer, on one line and in any order:

  RATING     1 … 10      the rating
  STATUS     p           pending
             c           in progress (current)
             t           finished (through)
             a           dropped (abandoned)
  FAVORITE   f  / -f     favorite / not any more

  Enter      leaves it as it is and moves on
  ?          shows this guide again
  q          stops here; what you've answered is already saved

  Examples:  9 f     → rated 9, favorite and finished
             7 a     → rated 7 and dropped
             c       → in progress, no rating yet
  A rating without a status means finished, unless it already said in
  progress or dropped. The status words work too: pending, finished...

  Then, if the entry has nothing of yours written, it asks why it's on
  display: what it left you, good or bad. It goes at the top of the entry,
  as your opinion. Enter skips it.
"""

# La ayuda de cada script (--help), en una vitrina en ingles. En castellano
# sale su docstring, que es mas largo porque cuenta tambien el porque.
AYUDAS = {
    "nueva": """Adds a single work: it finds it, you pick it, and it writes the whole entry.

  scripts/nueva.py game "hollow knight"
  scripts/nueva.py film "parasite" --rating 10 --favorite
  scripts/nueva.py series "breaking bad"
  scripts/nueva.py album "in rainbows" --status "in progress"
  scripts/nueva.py book "the name of the wind"
  scripts/nueva.py https://store.steampowered.com/app/367520/Hollow_Knight/

With a link there's nothing to search or choose: it carries the id. Steam,
Letterboxd (also boxd.it), TVmaze, MusicBrainz, Open Library and Spotify
albums work, and so do IMDb, TMDB, FilmAffinity, MyAnimeList, AniList,
Goodreads, Apple Music, Deezer, Discogs, IGDB, HowLongToBeat, Wikipedia and
Wikidata links, which go through Wikidata. No source needs an API key.

What the source can't know is yours, and goes in the options.""",
    "repasar": """Goes entry by entry through the ones without a rating or status, and
asks. One line per entry: `9 f` is a 9 and a favorite, `t` is finished,
Enter skips it and `q` stops. Every answer is saved at once.""",
    "estado": """Says what's in the vault and what's missing: entries per room, how many
are drafts, which fields are empty, ratings, statuses and favorites.
--check only warns.""",
    "al-dia": """Runs, in order, everything the scripts know how to fill in: room, date
added, opinion, cover, year, author, tags, text, dates and author pages.
It only touches what's missing, so it can be run any time;
--offline does only what needs no network.""",
    "importar": """Brings in your collection from elsewhere, as drafts to review:

  scripts/importar.py letterboxd-rss YOUR_USERNAME
  scripts/importar.py letterboxd-watchlist YOUR_USERNAME
  scripts/importar.py steam ~/Downloads/games.html
  scripts/importar.py listenbrainz YOUR_USERNAME
  scripts/importar.py spotify-export ~/Downloads/spotify.zip
  scripts/importar.py book "dune"

Nothing that already exists is overwritten, so it can be run again.""",
    "autores": """Writes a page for every author with two works or more, so entries that
share a studio, director or artist are linked in Obsidian too.""",
    "datos": """Fills in year, author and tags from the source each entry already has an
id for (Steam, Letterboxd, TVmaze, MusicBrainz, Open Library). Never by
guessing from the title.""",
    "textos": """Writes the “What it's about” of entries that are still blank, quoted from
the same source that identifies them, in the language of the display.""",
    "portadas": """Downloads the covers that are missing, by the id the entry already has,
and saves them as webp.""",
    "enlazar": """Fills in, from Wikidata and only where empty, what links each entry to
the world and to the others: its Wikidata item, and `based_on` / `follows`
when the other work is on display too. Nothing needs an API key.""",
    "vistazo": """Builds the site with everything in it — drafts, hidden and private
entries, marked — and serves it locally, to see it before publishing.""",
    "cuando": """Fills in, only where empty, when you finished or started each piece,
from the sites that log it: finished_on for films (Letterboxd diary, RSS or
export) and books (Goodreads "read" shelf), started_on for games (first Steam
achievement, by month) and albums (first listen on ListenBrainz or in Spotify's
extended history). Accounts can live in vitrine.local.json,
which git ignores.""",
}
