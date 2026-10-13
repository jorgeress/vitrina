# Por hacer

Lo que queda, separado en lo que hay que hacer para que funcione lo que ya
está, lo que solo puedo escribir yo y lo que se puede añadir. Al día del 13 de
octubre de 2026, con 210 fichas.

## Hecho desde la lista anterior

Privacidad en tres niveles (`draft`, `hidden` entero o por campos, y la carpeta
`privado/`), grupos hechos a mano (el anime se resolvió así: *Anime y manga*),
el anuario con `finished_on`, una tarjeta para compartir cada ficha, comparar
con un fichero, y Vitrine como plantilla en castellano o en inglés
(`scripts/empezar.py`, la web y los scripts en los dos idiomas).

## Para que funcione lo que ya está

- **Subir `main`.** Es lo que publica la web nueva.
- **Crear la etiqueta `nueva-pieza` en el repo.** La plantilla del Issue la
  pone, y la Action solo corre con los Issues que la llevan; si la etiqueta no
  existe, GitHub no la aplica y el Issue se queda sin contestar. Una vez:
  `gh label create nueva-pieza --description "Añadir una obra a la vitrina"`.
- **Probar el Issue de verdad** después del primer despliegue: uno con un
  enlace que ya esté (no toca nada) y otro con uno nuevo, con grupo y fecha.
- **Comprobar la web publicada**: que las direcciones viejas abren
  (`juegos/golf-it!`, `tags/action`, `index.xml`), que al pegar el enlace de una
  ficha en un chat sale su tarjeta, y que instalarla como app saca *Vitrina* en
  el menú de Compartir.
- **Marcar el repo como plantilla**, si quieres que otros puedan usarlo con un
  botón: *Settings → General → Template repository*. Sin eso se puede igual con
  un fork.

## Lo que solo puedo escribir yo

- **Las cartelas.** Hay cinco y cuatro son el texto de prueba (*Hollow Knight
  Silksong*, *Eternal Sunshine of the Spotless Mind*, *In Rainbows*, *Breaking
  Bad*). En la portada y en las tarjetas se ven mucho. `scripts/repasar.py` las
  pide una a una.
- **Las notas.** 43 de 210 tienen. Sin nota, el orden «por aprecio» y las
  cifras se quedan cojos.
- **Los estados.** Casi todo es `finished`; no hay nada `in-progress`, así que
  esa parte de los filtros está vacía.
- **Las fechas de terminado.** El anuario solo tiene 2026, que es el año en que
  entró todo. Con `finished_on` en lo que recuerdes (basta el año) aparecen los
  demás.
- **La presentación de la portada**, el primer párrafo de `content/index.md`.
  El borrador: «Una vitrina de lo que juego, veo, leo y escucho. No todo lo que
  pasa por mis manos: lo que se queda. Cada pieza lleva su cartela con lo que
  me dejó, y juntas dicen de mí más de lo que yo sabría contar.»
- **Más grupos**, si quieres: el de *Anime y manga* es el ejemplo.
- **Lo que no encuentran los scripts.** *Fortnite* no tiene portada (en
  Wikipedia solo está el logo) y quedan discos sin géneros: *DISOBEY VOL. II*,
  *Million Dollar Baby*, *Konbanwa* y *Wild Heart*. A mano, o se quedan así:
  antes vacío que equivocado.

## Lo que se puede añadir

De más a menos útil, a mi juicio.

- **La fecha de terminado desde Letterboxd.** El diario guarda el día en que
  viste cada película: `importar.py letterboxd-rss` podría escribirla en
  `finished_on`, y el anuario de películas se llenaría solo.
- **Importar solo cada noche.** Una Action programada que pase
  `importar.py letterboxd-rss` y `listenbrainz` y después `al-dia.py`, y abra
  un PR con los borradores nuevos para revisarlos.
- **«Me llegó por».** Un campo con quién te lo recomendó o de dónde salió. Con
  el tiempo, una página por persona. Se puede empezar ya con grupos («Lo que me
  recomendó Pablo»), sin campo nuevo.
- **«Me llevó a».** Un enlace de una obra a la siguiente que descubriste por
  ella; la constelación lo dibujaría con flechas.
- **Los docs en inglés.** El README está en los dos idiomas; `docs/scripts.md`
  y `docs/importar.md`, solo en castellano.
- **Más letras para las tarjetas.** Los títulos en japonés bajan su fuente de
  Google Fonts (Noto Sans JP); uno en coreano saldría con cuadros. Habría que
  elegir la Noto de cada alfabeto.
- **Más idiomas.** En la web es copiar el diccionario de `web/src/i18n.ts`. En
  los scripts, además de copiar `mensajes_en.py`, `_()` de `vitrina.py` tendría
  que elegir el catálogo por idioma, que hoy es castellano o inglés; y su
  entrada en `IDIOMAS` de `scripts/empezar.py`.
