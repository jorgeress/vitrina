# Por hacer

Lo que queda, separado en lo que hay que hacer para que lo que ya está
funcione, lo que solo puedo escribir yo y lo que se puede añadir. Al día del
13 de octubre de 2026, con 210 fichas.

## Para que funcione lo que ya está

- **Crear la etiqueta `nueva-pieza` en el repo.** La plantilla del Issue la
  pone, y la Action solo corre con los Issues que la llevan; si la etiqueta no
  existe, GitHub no la aplica y el Issue se queda sin contestar. Una vez:
  `gh label create nueva-pieza --description "Añadir una obra a la vitrina"`.
- **Probar el Issue de verdad** después del primer despliegue: uno con un
  enlace que ya esté (no toca nada) y otro con uno nuevo.
- **Comprobar la web publicada**: que las direcciones viejas abren
  (`juegos/golf-it!`, `tags/action`, `index.xml`) y que instalarla como app
  en el móvil saca *Vitrina* en el menú de Compartir.

## Lo que solo puedo escribir yo

- **Las cartelas.** Hay cinco y cuatro son el texto de prueba (*Hollow Knight
  Silksong*, *Eternal Sunshine of the Spotless Mind*, *In Rainbows*, *Breaking
  Bad*). En la portada se ven mucho. `scripts/repasar.py` las pide una a una.
- **Las notas.** 43 de 210 tienen. Sin nota, el orden «por aprecio» y las
  cifras se quedan cojos.
- **Los estados.** Casi todo es `terminado`; no hay nada `en curso`, así que
  esa parte de los filtros está vacía.
- **La presentación de la portada**, el primer párrafo de `content/index.md`.
  El borrador: «Una vitrina de lo que juego, veo, leo y escucho. No todo lo que
  pasa por mis manos: lo que se queda. Cada pieza lleva su cartela con lo que
  me dejó, y juntas dicen de mí más de lo que yo sabría contar.»
- **Lo que no encuentran los scripts.** *Fortnite* no tiene portada (en
  Wikipedia solo está el logo) y quedan discos sin géneros: *DISOBEY VOL. II*,
  *Million Dollar Baby*, *Konbanwa* y *Wild Heart*. A mano, o se quedan así:
  antes vacío que equivocado.

## Lo que se puede añadir

De más a menos útil, a mi juicio.

- **Importar solo cada noche.** Una Action programada que pase
  `importar.py letterboxd-rss` y `listenbrainz` y después `al-dia.py`, y abra
  un PR con los borradores nuevos para revisarlos. Todo lo que hace falta ya
  existe; es juntarlo en un workflow.
- **«Me llegó por».** Un campo con quién te lo recomendó o de dónde salió. En
  la ficha sale como una línea más, y con el tiempo una página por persona
  dibuja la gente que te ha ido formando el gusto.
- **«Me llevó a».** Un enlace de una obra a la siguiente que descubriste por
  ella. La constelación ya junta por autor y por tags; esto dibujaría el
  camino, con flechas.
- **Épocas.** Una etiqueta como `epoca/instituto` o `epoca/2026`, con su
  página, para ver qué te acompañaba en cada momento.
- **Tu año en la vitrina.** Cuando el campo `alta` lleve un año de historia: lo
  que entró ese año, por sala, con sus mejores notas. Sale de lo que ya hay.
- **Una imagen para compartir cada ficha.** Ahora un enlace a una ficha se ve
  en WhatsApp o en Discord con la portada suelta; una tarjeta con la portada, el
  título y la nota, hecha al construir, se vería como lo que es.
- **Portadas a su tamaño.** Se publican tal cual las deja `portadas.py`
  (6,5 MB en total). Sacar una versión pequeña para las rejillas aligeraría las
  salas en el móvil.
- **Comparar contra una vitrina guardada.** La página de comparar lee el
  `vitrina.json` de otra web; podría aceptar también el fichero, para
  comparar con alguien que no la tenga publicada.
- **Vitrine, para que la use cualquiera.** La herramienta en inglés y el
  contenido en el idioma de cada uno: los textos de la interfaz en un solo
  fichero por idioma, y el nombre, el autor y la dirección en uno de
  configuración, en vez de repartidos por `astro.config.mjs`, `src/repo.ts` y
  las páginas. Con eso se puede marcar el repo como plantilla.
- **El anime.** Sigue abierto si va como serie con la etiqueta `anime` (lo de
  ahora) o con sala propia.
