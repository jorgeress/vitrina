#!/usr/bin/env python3
"""Las pruebas de los scripts, sin red: python3 scripts/pruebas.py

No cubren todo a proposito. Cubren dos cosas: las funciones que deciden si una
ficha se rellena o se queda vacia, que es donde un fallo es silencioso, y los
casos concretos que ya mordieron una vez. Cada uno de esos lleva escrito de
donde salio, porque una prueba sin su historia es la primera que alguien borra
por parecer una tonteria.

Nada de aqui sale a la red. Lo que necesita una respuesta se la da a mano, que
ademas es la unica forma de probar el caso de la fuente caida.

Hace falta Pillow, como el resto de los scripts: portadas.py lo importa al
cargarse y de ahi cuelga media cadena de imports. Esta en requirements.txt.
"""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))

import datos
import importar
import autores
import textos
import vitrina as m
import nueva


class Cabeceras(unittest.TestCase):
    """Leer y escribir el YAML de una ficha sin romper lo que ya habia."""

    def test_lista_en_bloque_se_lee_como_lista(self):
        # Obsidian escribe asi los tags en cuanto los tocas desde su editor de
        # propiedades. Si se leyeran como vacios, un script creeria que la
        # ficha no tiene tags y los pisaria.
        campos = m.frontmatter("---\ntags:\n  - accion\n  - rpg\nnota: 9\n---\n")
        self.assertEqual(campos["tags"], ["accion", "rpg"])
        self.assertEqual(campos["nota"], "9")

    def test_lista_vacia_cuenta_como_campo_sin_poner(self):
        self.assertTrue(m.vacio("[]"))
        self.assertTrue(m.vacio([]))
        self.assertTrue(m.vacio(None))
        self.assertFalse(m.vacio("algo"))
        self.assertFalse(m.vacio(["accion"]))

    def test_una_lista_se_escribe_en_bloque(self):
        # escribir_ficha reventaba con los tags que trae la ficha de Steam
        # porque no sabia escribir una lista. Ahora hay una sola funcion que
        # escribe una linea de cabecera y la usan los dos sitios que escriben.
        self.assertEqual(m.linea_yaml("tags", ["accion", "rpg"]),
                         "tags:\n  - accion\n  - rpg")

    def test_un_valor_con_dos_puntos_se_entrecomilla(self):
        # Sin comillas, "Spider-Man: Brand New Day" parte el YAML en dos.
        self.assertEqual(m.yaml_valor("Spider-Man: Brand New Day"),
                         '"Spider-Man: Brand New Day"')

    def test_escribir_campos_no_deja_huerfana_la_lista_vieja(self):
        # Al cambiar una clave que tenia lista debajo, los elementos viejos se
        # quedarian colgando bajo la clave nueva si no se los lleva por delante.
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "f.md"
            md.write_text("---\ntipo: juego\ntags:\n  - viejo\n  - antiguo\n"
                          "nota: 9\n---\n\ncuerpo\n", encoding="utf-8")
            m.escribir_campos(md, {"tags": ["nuevo"]})
            texto = md.read_text(encoding="utf-8")
            self.assertNotIn("viejo", texto)
            self.assertNotIn("antiguo", texto)
            self.assertIn("- nuevo", texto)
            # Y lo que no se toca, no se mueve.
            self.assertIn("tipo: juego", texto)
            self.assertIn("nota: 9", texto)
            self.assertIn("cuerpo", texto)

    def test_escribir_campos_añade_una_clave_que_no_existia(self):
        # De esto vive la idea de que los scripts vayan completando la ficha:
        # datos.py y portadas.py añaden claves que la plantilla no trae.
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "f.md"
            md.write_text("---\ntipo: peli\n---\n\n", encoding="utf-8")
            m.escribir_campos(md, {"letterboxd": "harakiri"})
            self.assertIn("letterboxd: harakiri", md.read_text(encoding="utf-8"))

    def test_sin_cabecera_no_escribe_nada(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "f.md"
            md.write_text("una nota sin cabecera\n", encoding="utf-8")
            self.assertFalse(m.escribir_campos(md, {"nota": 9}))
            self.assertEqual(md.read_text(encoding="utf-8"),
                             "una nota sin cabecera\n")


class NombresYParecidos(unittest.TestCase):
    """Identificar una obra sin confundirla con otra que se llama parecido."""

    def test_el_titulo_de_verdad_se_guarda_cuando_no_cabe_en_el_fichero(self):
        # Un nombre de fichero no admite ":", asi que "Spider-Man: Brand New
        # Day" se quedaba sin los dos puntos y con eso ya no lo encontraba
        # ningun catalogo.
        self.assertEqual(m.nombre_de_fichero("Spider-Man: Brand New Day"),
                         "Spider-Man Brand New Day")
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("pelis", "Spider-Man: Brand New Day", {"tipo": "peli"})
            ficha = Path(tmp) / "pelis" / "Spider-Man Brand New Day.md"
            self.assertIn('title: "Spider-Man: Brand New Day"',
                          ficha.read_text(encoding="utf-8"))

    def test_la_misma_obra_escrita_distinto_no_se_duplica(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            self.assertIsNotNone(m.escribir_ficha("pelis", "Parásitos", {"tipo": "peli"}))
            self.assertIsNone(m.escribir_ficha("pelis", "Parasitos", {"tipo": "peli"}))

    def test_una_ficha_que_ya_existe_nunca_se_pisa(self):
        # De esto depende poder repetir un volcado para recoger solo lo nuevo.
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("juegos", "Portal", {"tipo": "juego", "nota": 10})
            ficha = Path(tmp) / "juegos" / "Portal.md"
            antes = ficha.read_text(encoding="utf-8")
            self.assertIsNone(m.escribir_ficha("juegos", "Portal", {"tipo": "juego"}))
            self.assertEqual(ficha.read_text(encoding="utf-8"), antes)

    def test_lo_que_se_parece_se_avisa_pero_no_se_descarta(self):
        # "Portal" contiene a "Portal 2" y son dos juegos distintos: se avisa
        # y decide el humano.
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("juegos", "Portal", {"tipo": "juego"})
            self.assertTrue(m.parecidos("juegos", ["Portal 2"]))
            self.assertFalse(m.parecidos("juegos", ["Hades"]))

    def test_una_ficha_nueva_entra_en_borrador_y_con_tags_vacios(self):
        # El invariante del README: a la web solo llega lo ascendido a mano.
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("juegos", "Hades", {"tipo": "juego"})
            texto = (Path(tmp) / "juegos" / "Hades.md").read_text(encoding="utf-8")
            self.assertIn("draft: true", texto)
            self.assertIn("tags: []", texto)

    def test_encaja_admite_que_el_titulo_baile_pero_no_otra_pelicula(self):
        # El buscador de Wikipedia siempre devuelve algo, aunque no tenga nada
        # que ver: sin esta comprobacion una ficha se queda con el cartel de
        # otra pelicula.
        self.assertTrue(m.encaja("Kill Bill Vol. 1", "Kill Bill: Volumen 1"))
        self.assertFalse(m.encaja("Harakiri", "Zoolander"))
        self.assertFalse(m.encaja("", "lo que sea"))

    def _vault(self, tmp):
        m.VAULT = Path(tmp)
        self.addCleanup(setattr, m, "VAULT", m.RAIZ / "content")


class FuenteCaida(unittest.TestCase):
    """Una fuente caida no es "no hay resultados", y no se pueden confundir.

    pedir() devuelve None en los dos casos, y confundirlos manda a buscar el
    error donde no esta. Los buscadores devuelven None si no se ha podido
    preguntar y [] si de verdad no hay nada.
    """

    def test_sin_respuesta_devuelve_none(self):
        self._pedir(lambda *a, **k: None)
        self.assertIsNone(nueva.buscar_juego("lo que sea", 5))
        self.assertIsNone(nueva.buscar_album("lo que sea", 5))

    def test_respuesta_vacia_devuelve_lista_vacia(self):
        self._pedir(lambda *a, **k: [])
        self.assertEqual(nueva.buscar_juego("lo que sea", 5), [])
        self._pedir(lambda *a, **k: {"release-groups": []})
        self.assertEqual(nueva.buscar_album("lo que sea", 5), [])

    def test_un_juego_sin_appid_no_entra(self):
        # Sin appid la caratula no se puede bajar y la ficha se queda a medias.
        self._pedir(lambda *a, **k: [{"name": "Con id", "appid": 400},
                                     {"name": "Sin id"}])
        self.assertEqual([c["titulo"] for c in nueva.buscar_juego("x", 5)],
                         ["Con id"])

    def _pedir(self, falso):
        original = nueva.pedir
        nueva.pedir = falso
        self.addCleanup(setattr, nueva, "pedir", original)


class CancionesEnDiscos(unittest.TestCase):
    """Plegar las canciones guardadas en el disco que las lleva, y contarlas."""

    LIBRERIA = {"tracks": [
        {"artist": "Radiohead", "album": "In Rainbows", "track": "Nude"},
        {"artist": "Radiohead", "album": "In Rainbows", "track": "Reckoner"},
        {"artist": "Radiohead", "album": "In Rainbows", "track": "Videotape"},
        {"artist": "Portishead", "album": "Dummy", "track": "Roads"},
        {"artist": "Nick Drake", "album": "Pink Moon", "track": "Pink Moon"},
        {"artist": None, "album": None, "track": "una suelta sin disco"},
    ]}

    def test_cuenta_las_canciones_de_cada_disco(self):
        discos = importar.canciones_en_discos(self.LIBRERIA, {})
        self.assertEqual(discos["In Rainbows"]["favoritas"], 3)
        self.assertEqual(discos["Dummy"]["favoritas"], 1)
        self.assertEqual(discos["In Rainbows"]["autor"], "Radiohead")

    def test_una_cancion_sin_disco_no_inventa_un_disco(self):
        # Antes vacio que equivocado: sin nombre de album no hay nada que contar.
        discos = importar.canciones_en_discos(self.LIBRERIA, {})
        self.assertEqual(len(discos), 3)
        self.assertNotIn(None, discos)

    def test_admite_las_dos_formas_en_que_spotify_nombra_las_claves(self):
        discos = importar.canciones_en_discos(
            {"tracks": [{"albumName": "Dummy", "artistName": "Portishead"}]}, {})
        self.assertEqual(discos["Dummy"]["favoritas"], 1)
        self.assertEqual(discos["Dummy"]["autor"], "Portishead")

    def test_sin_la_clave_tracks_no_revienta(self):
        self.assertEqual(importar.canciones_en_discos({"albums": []}, {}), {})
        self.assertEqual(importar.canciones_en_discos({"tracks": None}, {}), {})

    def test_el_umbral_decide_que_disco_es_favorito(self):
        discos = importar.canciones_en_discos(self.LIBRERIA, {})
        args = SimpleNamespace(completo=False, min_horas=8, min_nota=8,
                               min_favoritas=3)
        dentro, fuera = importar.criba(discos, args)
        self.assertEqual(list(dentro), ["In Rainbows"])
        self.assertEqual(sorted(fuera), ["Dummy", "Pink Moon"])

    def test_con_completo_entran_todos(self):
        discos = importar.canciones_en_discos(self.LIBRERIA, {})
        args = SimpleNamespace(completo=True, min_horas=8, min_nota=8,
                               min_favoritas=3)
        dentro, fuera = importar.criba(discos, args)
        self.assertEqual(len(dentro), 3)
        self.assertEqual(fuera, {})


class TextosDeDiscos(unittest.TestCase):
    """La lista de canciones de un disco.

    Sin favoritas por cancion: se probaron, con una estrella al final de la
    linea, y se quitaron a peticion suya. Marcarlas exigia editar el fichero y
    pasar un script, y eso no lo puede hacer nadie desde la web publicada, que
    es estatica. Los favoritos son de disco entero, con el campo `favorito`.
    """

    def test_la_lista_sale_numerada_y_en_orden(self):
        self.assertEqual(textos.cuerpo_disco(["Nude", "Reckoner", "Videotape"]),
                         "## Canciones\n\n1. Nude\n2. Reckoner\n3. Videotape")

    def test_una_cancion_repetida_se_lista_las_dos_veces(self):
        # La edicion de My Beautiful Dark Twisted Fantasy que lista MusicBrainz
        # trae "Runaway" dos veces: es lo que dice la edicion, y se respeta.
        cuerpo = textos.cuerpo_disco(["Power", "Runaway", "Blame Game", "Runaway"])
        self.assertIn("2. Runaway", cuerpo)
        self.assertIn("4. Runaway", cuerpo)

    def test_un_disco_sin_canciones_no_revienta(self):
        self.assertEqual(textos.cuerpo_disco([]), "## Canciones\n\n")


class LoQueEscribeEl(unittest.TestCase):
    """Su parrafo es lo unico de una ficha que no se puede volver a bajar.

    Por eso `--force` puede rehacer la cita y la lista de canciones, pero no
    puede tocar lo que haya escrito el. Sin esto, una pasada con --force le
    borraba el texto sin avisar.
    """

    def test_force_no_le_borra_el_parrafo_a_una_pelicula(self):
        cuerpo = ("Me rei con esta desde los catorce.\n\n"
                  "> [!quote] De qué va\n> Algo.\n>\n> → [x](y)\n")
        self.assertEqual(textos.lo_suyo(cuerpo), "Me rei con esta desde los catorce.")

    def test_force_no_le_borra_el_parrafo_a_un_disco(self):
        # En un disco lo generado es la lista entera desde su encabezado, asi
        # que sin esto la segunda pasada duplicaria la lista y se comeria lo suyo.
        cuerpo = "Mi disco favorito.\n\n## Canciones\n\n1. Una\n2. Otra\n"
        self.assertEqual(textos.lo_suyo(cuerpo), "Mi disco favorito.")

    def test_una_ficha_sin_nada_suyo_da_vacio(self):
        self.assertEqual(textos.lo_suyo("> [!quote] De qué va\n> Algo.\n"), "")
        self.assertEqual(textos.lo_suyo(""), "")


class AutoresYComas(unittest.TestCase):
    """Partir el campo `autor` sin inventarse estudios que no existen."""

    def test_una_empresa_con_coma_no_son_dos_autores(self):
        # Mordio de verdad: partiendo por comas a secas, "Inc." salia como el
        # estudio con mas juegos de la coleccion, cinco, por delante de
        # FromSoftware. Son sufijos de empresa, no autores.
        self.assertEqual(autores.separar("FromSoftware, Inc."), ["FromSoftware, Inc."])
        self.assertEqual(autores.separar("CyberConnect2 Co. Ltd."),
                         ["CyberConnect2 Co. Ltd."])

    def test_dos_directores_si_son_dos_autores(self):
        self.assertEqual(autores.separar("Mike Johnson, Tim Burton"),
                         ["Mike Johnson", "Tim Burton"])

    def test_una_empresa_y_una_persona_a_la_vez(self):
        # El caso peor de los dos juntos: "Nicalis, Inc." es uno y Edmund otro.
        self.assertEqual(autores.separar("Nicalis, Inc., Edmund McMillen"),
                         ["Nicalis, Inc.", "Edmund McMillen"])

    def test_un_autor_ya_enlazado_se_lee_como_su_nombre(self):
        # De esto depende poder volver a pasar el script sin acabar con
        # enlaces dentro de enlaces.
        self.assertEqual(
            autores.separar("[[autores/Radiohead|Radiohead]]"), ["Radiohead"])
        self.assertEqual(
            autores.separar("[[autores/FromSoftware, Inc|FromSoftware, Inc.]]"),
            ["FromSoftware, Inc."])

    def test_sin_autor_no_devuelve_nada(self):
        self.assertEqual(autores.separar(""), [])
        self.assertEqual(autores.separar(None), [])


class TextosCitados(unittest.TestCase):
    """Lo que no es suyo sale citado y enlazado."""

    def test_la_cita_de_steam_enlaza_su_ficha_de_la_tienda(self):
        # Steam no da ninguna licencia: la cita con su fuente es lo que la
        # ampara, asi que un texto suyo sin enlace no debe poder salir.
        cuerpo = textos.cita("Un juego de prueba.", textos.credito_steam(1))
        self.assertTrue(cuerpo.startswith("> [!quote] De qué va"))
        self.assertTrue(cuerpo.endswith("> → [Steam](https://store.steampowered.com/app/1/)"))
        for linea in cuerpo.splitlines():
            self.assertTrue(linea.startswith(">"), f"linea fuera del callout: {linea}")

    def test_la_cita_de_wikipedia_nombra_la_licencia(self):
        # CC BY-SA pide enlazar la fuente y decir la licencia. El enlace al
        # articulo cubre a los autores, porque su historial es la lista.
        credito = textos.credito_wikipedia("El viaje de Chihiro")
        self.assertIn("es.wikipedia.org/wiki/El_viaje_de_Chihiro", credito)
        self.assertIn("CC BY-SA 4.0", credito)

    def test_las_etiquetas_html_de_steam_no_llegan_a_la_ficha(self):
        self.assertEqual(textos.limpio("Uno<br>y <strong>dos</strong> &amp; tres"),
                         "Uno y dos & tres")


class Etiquetas(unittest.TestCase):
    def test_un_genero_se_vuelve_tag_sin_perder_los_acentos(self):
        # "accion" al lado de "aventura" canta: son etiquetas que se leen.
        self.assertEqual(datos.etiqueta("  Acción y Aventura "), "acción-y-aventura")
        self.assertEqual(datos.etiqueta(None), "")

    def test_sacar_se_queda_con_la_primera_clave_que_traiga_algo(self):
        self.assertEqual(importar.sacar({"albumName": "X"}, "album", "albumName"), "X")
        self.assertEqual(importar.sacar({"album": "", "albumName": "X"},
                                        "album", "albumName"), "X")
        self.assertIsNone(importar.sacar({}, "album", "albumName"))


class GenerosDeLibro(unittest.TestCase):
    """La lista blanca de Open Library, que es la unica fuente que va al reves.

    Las otras tres cogen los primeros generos y los traducen. Aqui no se puede:
    `subject` es la catalogacion de una biblioteca, sin orden y con de todo
    dentro, asi que se busca cuales de los sesenta estan en la tabla. Estas
    pruebas son los casos con los que se ajusto la tabla, y estan para que no se
    le vuelvan a meter los generos blandos que la hacian fallar.
    """

    def test_de_sesenta_subjects_solo_salen_los_que_son_genero(self):
        # Los de `L'etranger`, recortados. Estan mezclados el genero, el tema
        # del argumento, el idioma de una edicion y la ficha de catalogo.
        subjects = ["Philosophical Novels", "Murder", "Fiction", "French",
                    "Large type books", "Young men", "Death",
                    "Fictional Works [Publication Type]", "Translations into English"]
        self.assertEqual(datos.generos_de_subjects(subjects), ["filosofía"])

    def test_lo_que_no_esta_en_la_tabla_no_se_escribe(self):
        # El caso que decide el diseño: antes de dejarla asi, "adventure
        # stories" y "classics" estaban dentro y le ponian `aventura` a
        # `El extranjero`. Un tag inventado por una maquina no se ve y se queda.
        self.assertEqual(datos.generos_de_subjects(["Adventure stories", "Classics",
                                                    "History", "Satire"]), [])
        self.assertEqual(datos.generos_de_subjects([]), [])
        self.assertEqual(datos.generos_de_subjects(None), [])

    def test_una_cabecera_de_bisac_se_parte_para_leerle_el_genero(self):
        # De aqui sale el genero de la mitad de los libros. La editorial no
        # declara `horror`: declara "Fiction, Horror", y buscando la cadena
        # entera se tiraba entera. Open Library las escribe de las dos formas,
        # con comas y con barras, y las dos tienen que valer.
        self.assertEqual(datos.generos_de_subjects(["Fiction, Horror"]), ["terror"])
        self.assertEqual(
            datos.generos_de_subjects(["Fiction / Science Fiction / Hard Science Fiction"]),
            ["ciencia-ficción"])
        self.assertEqual(datos.generos_de_subjects(["Fiction, Mystery & Detective, General"]),
                         ["misterio"])

    def test_un_subject_suelto_no_se_parte_aunque_lleve_coma(self):
        # El guardarrail de lo de arriba. `1984` trae "fantasy" por su cuenta,
        # de que alguien lo puso en un estante, y salia de novela fantastica.
        # Solo se parte lo que empieza por una categoria de BISAC.
        self.assertEqual(datos.generos_de_subjects(["fantasy"]), [])
        self.assertEqual(datos.generos_de_subjects(["Comic books, strips"]), [])
        self.assertEqual(datos.generos_de_subjects(["Romans, nouvelles"]), [])

    def test_dos_nombres_del_mismo_genero_dan_un_tag_y_no_dos(self):
        # Casi todo libro de ciencia-ficcion trae varios de estos a la vez.
        self.assertEqual(
            datos.generos_de_subjects(["Science Fiction", "sci-fi", "science-fiction"]),
            ["ciencia-ficción"])

    def test_los_tags_caen_donde_los_de_las_pelis_y_los_juegos(self):
        # De esto vive una pagina de etiqueta: si un libro de terror pusiera
        # `horror` y una peli `terror`, serian dos paginas con una obra cada
        # una en vez de una con las dos.
        destinos = set(datos.GENEROS_OPENLIBRARY.values())
        conocidos = set(datos.GENEROS_LETTERBOXD.values())
        # Los que no comparte con las pelis son los que el cine no tiene.
        self.assertEqual(sorted(destinos - conocidos),
                         ["biografía", "filosofía", "poesía"])

    def test_un_libro_sin_coverid_no_pregunta_por_titulo(self):
        # La raya del script: sin el id no hay obra, y buscar "Noches blancas"
        # a ver que sale es justo lo que no hace ninguna de las cuatro fuentes.
        def no_llamar(*a, **k):
            self.fail("ha salido a la red sin id")
        original = datos.pedir
        datos.pedir = no_llamar
        self.addCleanup(setattr, datos, "pedir", original)
        valores, detalle = datos.datos_libro("Noches blancas", {}, None)
        self.assertEqual(valores, {})
        self.assertIn("coverid", detalle)


class Coherencia(unittest.TestCase):
    """Que la vault y lo que los scripts esperan de ella no se separen."""

    def test_cada_seccion_escribe_el_tipo_que_su_base_filtra(self):
        # Si una .base filtra por un tipo que ningun script escribe, la seccion
        # sale vacia en la web sin que falle nada.
        bases = {"juegos": "Juegos", "pelis": "Peliculas",
                 "libros": "Libros", "musica": "Musica"}
        for carpeta, base in bases.items():
            ruta = m.RAIZ / "content" / f"{base}.base"
            if not ruta.exists():
                continue
            texto = ruta.read_text(encoding="utf-8")
            self.assertIn(f'note.tipo == "{m.SECCIONES[carpeta]}"', texto,
                          f"{base}.base no filtra por el tipo que escribe {carpeta}")

    def test_las_vistas_de_estado_filtran_por_estados_que_existen(self):
        # Mismo riesgo que el tipo, y mas facil de que pase: las dos ultimas
        # vistas de cada seccion --lo terminado y lo que queda-- filtran por un
        # valor escrito a mano. Con una letra de mas la pestaña sale vacia y no
        # falla nada.
        for base in ("Peliculas", "Libros", "Musica"):
            ruta = m.RAIZ / "content" / f"{base}.base"
            if not ruta.exists():
                continue
            texto = ruta.read_text(encoding="utf-8")
            filtrados = set(re.findall(r'note\.estado == "([^"]*)"', texto))
            self.assertTrue(filtrados, f"{base}.base no filtra por estado")
            for estado in filtrados:
                self.assertIn(estado, m.ESTADOS,
                              f'{base}.base filtra por "{estado}", que no existe')

    def test_juegos_reparte_por_las_horas_y_no_por_el_estado(self):
        # La excepcion de las cuatro secciones, y esta puesta a proposito: en
        # juegos no hay `estado` que mirar --Steam sabe cuanto has jugado, no si
        # lo terminaste-- asi que sus dos ultimas vistas van por `horas`. Si
        # alguna volviera a filtrar por estado, saldria vacia, que es como no
        # estar.
        texto = (m.RAIZ / "content" / "Juegos.base").read_text(encoding="utf-8")
        self.assertIn("- note.horas", texto)
        self.assertNotIn("note.estado", texto)

    def test_ninguna_ficha_se_inventa_un_estado(self):
        # Una ficha con un estado fuera de la lista no sale ni en la vista de lo
        # terminado ni en la de lo que queda: solo en la galeria, con todo lo
        # demas, que es donde no se nota.
        for carpeta in m.SECCIONES:
            for ficha in (m.RAIZ / "content" / carpeta).glob("*.md"):
                if ficha.stem == "index":
                    continue
                estado = m.frontmatter(ficha.read_text(encoding="utf-8")).get("estado")
                if m.vacio(estado):
                    continue
                self.assertIn(estado, m.ESTADOS,
                              f"{ficha.name} dice estado: {estado}")

    def test_las_fichas_de_la_vault_llevan_un_tipo_conocido(self):
        for carpeta, tipo in m.SECCIONES.items():
            for ficha in (m.RAIZ / "content" / carpeta).glob("*.md"):
                if ficha.stem == "index":
                    continue
                campos = m.frontmatter(ficha.read_text(encoding="utf-8"))
                self.assertEqual(campos.get("tipo"), tipo,
                                 f"{ficha.name} no dice tipo: {tipo}")

    def test_ninguna_ficha_apunta_a_una_portada_que_no_existe(self):
        # Una portada que falta no rompe el build: deja un hueco en la galeria.
        for carpeta in m.SECCIONES:
            for ficha in (m.RAIZ / "content" / carpeta).glob("*.md"):
                portada = m.frontmatter(ficha.read_text(encoding="utf-8")).get("portada")
                if not portada or not portada.startswith("[["):
                    continue
                nombre = portada.strip("[]")
                self.assertTrue((m.PORTADAS / nombre).exists(),
                                f"{ficha.name} apunta a {nombre}, que no esta")


    def test_las_paginas_de_autor_dicen_lo_que_dice_la_vault(self):
        # Las de content/autores/ son material derivado que vive dentro de la
        # fuente, y eso solo se sostiene mientras alguien se acuerde de volver a
        # pasar autores.py. No falla nada si no se acuerda: la pagina se queda
        # con las obras de la ultima pasada, la ficha nueva no aparece en ella y
        # el grafo la deja suelta, que es como no haberla añadido.
        #
        # Y pasa justo al crecer, que es cuando toca. Hay 86 firmas con una sola
        # obra, o sea 86 paginas esperando a que llegue la segunda: cada tanda
        # que se mete estrena unas cuantas y le añade obras a las que ya estan.
        mapa = autores.obras_por_autor()
        esperadas = {m.nombre_de_fichero(a): autores.pagina(a, o)
                     for a, o in mapa.items() if len(o) >= 2}
        carpeta = m.RAIZ / "content" / "autores"
        en_disco = {md.stem for md in carpeta.glob("*.md")} if carpeta.exists() else set()

        faltan = sorted(set(esperadas) - en_disco)
        self.assertFalse(faltan, "sin pagina de autor y con dos obras o mas: "
                                 f"{faltan}. Pasa scripts/autores.py")
        sobran = sorted(en_disco - set(esperadas))
        self.assertFalse(sobran, "paginas de autor que ya no agrupan dos obras: "
                                 f"{sobran}. Pasa scripts/autores.py")
        for nombre, contenido in esperadas.items():
            actual = (carpeta / f"{nombre}.md").read_text(encoding="utf-8")
            self.assertEqual(actual, contenido,
                             f"{nombre}.md no lista lo que hay en la vault. "
                             "Pasa scripts/autores.py")


if __name__ == "__main__":
    unittest.main(verbosity=2)
