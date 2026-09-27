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

import io
import json
import re
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))

import datos
import estado
import importar
import autores
import portadas
import repasar
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


class CifrasDelReadme(unittest.TestCase):
    """El bloque de cifras del README sale de la vault, no de contar a mano.

    Escrito a mano se quedaba viejo solo: llego a decir 155 fichas cuando ya
    habia 210. Las cifras que no pueden salir de aqui no se ponen en ningun
    sitio.
    """

    RESUMEN = ("FICHAS\n  juegos  46\n\n"
               "EN LA WEB  ████  210 de 210\n\n"
               "SIN RELLENAR\n  nota  164\n\n"
               "NOTAS      10:38  9:2\n\n"
               "FAVORITOS  ██  21 de 210\n  juegos  6\n")

    def test_el_bloque_es_el_resumen_recortado(self):
        bloque = estado.bloque_readme(self.RESUMEN)
        self.assertIn("FICHAS", bloque)
        self.assertIn("SIN RELLENAR", bloque)
        # De FAVORITOS solo el titular; el reparto por secciones no ilustra nada.
        self.assertIn("FAVORITOS  ██  21 de 210", bloque)
        self.assertNotIn("juegos  6", bloque)
        # Y lo que el README no enseña no se cuela.
        self.assertNotIn("EN LA WEB", bloque)
        self.assertNotIn("NOTAS", bloque)

    def test_el_bloque_cae_donde_estaba_y_no_toca_el_resto(self):
        texto = "# Vitrina\n\n```\nFICHAS\n  viejo\n```\n\nLo de después.\n"
        nuevo = estado.BLOQUE_RE.sub(
            lambda _: estado.bloque_readme(self.RESUMEN), texto, count=1)
        self.assertIn("juegos  46", nuevo)
        self.assertNotIn("viejo", nuevo)
        self.assertTrue(nuevo.startswith("# Vitrina"))
        self.assertTrue(nuevo.endswith("Lo de después.\n"))

    def test_un_readme_sin_bloque_no_se_toca(self):
        # Antes que meter el bloque donde no va, no se escribe y se dice.
        self.assertIsNone(estado.BLOQUE_RE.search("# Vitrina\n\nSin cifras.\n"))


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

    def test_dos_discos_japoneses_no_caen_en_el_mismo_fichero(self):
        # "アダンの風" y "悪の華" no dejan ni una letra al pasar a ASCII, asi
        # que los dos daban "sin titulo.md": el primero se creaba con un nombre
        # que no es de nadie y el segundo ya no se creaba. El nombre en latino
        # lo dice MusicBrainz, y el titulo de verdad se queda en `title`.
        self.assertTrue(m.sin_letras_latinas("アダンの風"))
        self.assertFalse(m.sin_letras_latinas("El madrileño"))
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("musica", "アダンの風", {"tipo": "album"},
                             fichero="Windswept Adan")
            m.escribir_ficha("musica", "悪の華", {"tipo": "album"},
                             fichero="Aku no Hana")
            nombres = sorted(p.stem for p in (Path(tmp) / "musica").glob("*.md"))
            self.assertEqual(nombres, ["Aku no Hana", "Windswept Adan"])
            ficha = Path(tmp) / "musica" / "Windswept Adan.md"
            self.assertIn("title: アダンの風", ficha.read_text(encoding="utf-8"))

    def test_un_titulo_aparte_no_se_come_la_clave_de_encima(self):
        # La linea de `title` se insertaba delante antes de poner el `tags: []`,
        # y el indice de tags se calculaba sin contarla: caia sobre `portada` y
        # lo dejaba en "tags: []". La cabecera salia con dos `tags:` y sin
        # portada, que es YAML invalido: Quartz no construye esa ficha.
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            md = m.escribir_ficha("musica", "D>E>A>T>H>M>E>T>A>L",
                                  {"tipo": "album", "portada": None, "tags": None})
            cabecera = md.read_text(encoding="utf-8")
            self.assertEqual(cabecera.count("\ntags:"), 1)
            self.assertEqual(cabecera.count("\nportada:"), 1)
            self.assertIn("title: D>E>A>T>H>M>E>T>A>L", cabecera)

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

    def test_un_titulo_corto_no_avisa_contra_media_coleccion(self):
        # `normal` quita los espacios, asi que con "lo lleva dentro" bastaba que
        # "Pi" apareciera en mitad de otro titulo: importando una watchlist de
        # 632 peliculas el aviso salia lleno de parejas sin relacion. Uno tiene
        # que empezar por el otro, que es como se repite una obra de verdad.
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("pelis", "Pi", {"tipo": "peli"})
            self.assertFalse(m.parecidos("pelis", ["Scott Pilgrim vs. the World"]))
            self.assertTrue(m.parecidos("pelis", ["Pi Day"]))

    def test_la_misma_obra_con_subtitulo_si_avisa(self):
        # Por donde se repiten de verdad: el subtitulo, la edicion o el año.
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("juegos", "Dark Souls", {"tipo": "juego"})
            self.assertTrue(m.parecidos("juegos", ["Dark Souls Remastered"]))

    def test_una_ficha_nueva_entra_en_borrador_y_con_tags_vacios(self):
        # El invariante del README: a la web solo llega lo ascendido a mano.
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("juegos", "Hades", {"tipo": "juego"})
            texto = (Path(tmp) / "juegos" / "Hades.md").read_text(encoding="utf-8")
            self.assertIn("draft: true", texto)
            self.assertIn("tags: []", texto)

    def test_una_ficha_nueva_nace_con_su_fecha_de_alta(self):
        # De ella sale "Ultimas añadidas" en la portada. Sin fecha, la ficha
        # no llegaria nunca a esa lista por mucho que fuera la ultima.
        with tempfile.TemporaryDirectory() as tmp:
            self._vault(tmp)
            m.escribir_ficha("juegos", "Hades", {"tipo": "juego"})
            campos = m.frontmatter((Path(tmp) / "juegos" / "Hades.md").read_text(encoding="utf-8"))
            self.assertRegex(campos.get("alta", ""), r"^\d{4}-\d{2}-\d{2}$")

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

    def test_una_serie_sin_responder_no_se_confunde_con_ninguna(self):
        # TVmaze caido devuelve None, igual que Steam o MusicBrainz, y no una
        # lista vacia, que querria decir que esa serie no existe.
        self._pedir(lambda *a, **k: None)
        self.assertIsNone(nueva.buscar_serie("lo que sea", 5))
        self._pedir(lambda *a, **k: [])
        self.assertEqual(nueva.buscar_serie("lo que sea", 5), [])

    def test_un_juego_sin_appid_no_entra(self):
        # Sin appid la caratula no se puede bajar y la ficha se queda a medias.
        self._pedir(lambda *a, **k: [{"name": "Con id", "appid": 400},
                                     {"name": "Sin id"}])
        self.assertEqual([c["titulo"] for c in nueva.buscar_juego("x", 5)],
                         ["Con id"])

    def test_un_disco_sin_nombre_en_latino_se_para_en_vez_de_llamarse_nada(self):
        # "悪の華" no deja ni una letra al pasar a ASCII y MusicBrainz no le
        # conoce alias en ingles. Antes salia "sin titulo.md" con la portada
        # ".webp": una ficha que no se llama de nada, y una imagen que se
        # pisarian entre ellas todas las que cayeran ahi. Ahora se para y lo
        # pide, que como se llama en latino no se adivina.
        elegido = nueva.candidato("悪の華", year="1990", mbid="8d0a2aaa")
        self._pedir(lambda *a, **k: {"aliases": []})
        self.assertIsNone(nueva.nombre_latino("album", elegido))
        self._pedir(lambda *a, **k: {"aliases": [{"locale": "en",
                                                  "name": "Aku no Hana"}]})
        self.assertEqual(nueva.nombre_latino("album", elegido), "Aku no Hana")

    def _pedir(self, falso):
        # En los dos modulos: unos buscadores piden desde nueva.py y otros --el
        # de series-- desde el ayudante que vive en vitrina.py.
        for modulo in (nueva, m):
            original = modulo.pedir
            modulo.pedir = falso
            self.addCleanup(setattr, modulo, "pedir", original)


class BuscarSeries(unittest.TestCase):
    """El buscador de series: que no se equivoque de cual, ni de por que falla."""

    def test_un_404_no_se_reintenta_ni_se_cuenta_como_caida(self):
        # pedir() se tragaba el 404 igual que un corte de red: reintentaba tres
        # veces y devolvia None. Con un `tvmaze` mal copiado, datos.py decia
        # "TVmaze no responde" y mandaba a buscar el fallo a la red.
        llamadas = self._urlopen(404)
        self.assertEqual(m.pedir("https://x/shows/1", no_existe={}), {})
        self.assertIsNone(m.pedir("https://x/shows/1"))
        self.assertEqual(len(llamadas), 2)

    def test_un_429_se_reintenta(self):
        # TVmaze corta a las veinte peticiones en diez segundos.
        llamadas = self._urlopen(429)
        self.assertIsNone(m.pedir("https://x/shows/1", reintentos=3))
        self.assertEqual(len(llamadas), 3)

    def test_datos_distingue_id_inexistente_de_fuente_caida(self):
        self._serie(None)
        self.assertIn("no responde", datos.datos_serie("x", {"tvmaze": "1"}, None)[1])
        self._serie({})
        self.assertIn("no tiene ficha", datos.datos_serie("x", {"tvmaze": "1"}, None)[1])

    def test_lo_que_no_es_ficcion_va_al_final(self):
        # "hunter x hunter" trae los Winter X Games delante del anime del 99.
        self._buscar([{"id": 1, "name": "Winter X Games", "type": "Sports"},
                      {"id": 2, "name": "Hunter x Hunter", "type": "Animation"}])
        self.assertEqual([s["id"] for s in m.series_tvmaze("hunter x hunter")], [2, 1])

    def test_wikidata_solo_cuando_nada_se_llama_asi(self):
        # "el juego del calamar" no la encuentra TVmaze, que la tiene como
        # Squid Game; Wikidata si, por el titulo en español.
        pedidas = []
        original = m.series_wikidata
        m.series_wikidata = lambda q: pedidas.append(q) or [{"id": 9, "name": "Squid Game"}]
        self.addCleanup(setattr, m, "series_wikidata", original)

        self._buscar([{"id": 5, "name": "Breaking Bad"}])
        self.assertEqual([s["id"] for s in m.series_tvmaze("breaking bad")], [5])
        self.assertEqual(pedidas, [])

        self._buscar([])
        self.assertEqual([s["id"] for s in m.series_tvmaze("el juego del calamar")], [9])
        self._buscar(None)
        self.assertIsNone(m.series_tvmaze("el juego del calamar"))

    def test_la_pista_separa_las_dos_one_piece(self):
        # Las dos son Action y Adventure: con los generos solos no se sabia
        # cual era el anime y cual la de Netflix con actores.
        anime = {"type": "Animation", "genres": ["Action"],
                 "network": {"country": {"code": "JP"}}}
        actores = {"type": "Scripted", "genres": ["Action"], "language": "English",
                   "webChannel": {"name": "Netflix", "country": None}}
        self.assertEqual(nueva.pista_serie(anime), "JP · animación · Action")
        self.assertEqual(nueva.pista_serie(actores), "English · Action")

    def test_la_misma_serie_con_otro_nombre_no_entra_dos_veces(self):
        # "shingeki no kyojin" encuentra Attack on Titan, que ya estaba: el
        # nombre de fichero no coincide y el id si.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "series").mkdir()
            (Path(tmp) / "series" / "Attack on Titan.md").write_text(
                "---\ntipo: serie\ntvmaze: 919\n---\n", encoding="utf-8")
            original = nueva.VAULT
            nueva.VAULT = Path(tmp)
            self.addCleanup(setattr, nueva, "VAULT", original)
            self.assertEqual(nueva.ficha_con_id("series", {"tvmaze": 919}),
                             "Attack on Titan")
            self.assertIsNone(nueva.ficha_con_id("series", {"tvmaze": 920}))

    def _urlopen(self, codigo):
        import urllib.error
        llamadas = []

        def falso(req, timeout=None):
            llamadas.append(req)
            raise urllib.error.HTTPError(req.full_url, codigo, "", {}, io.BytesIO())

        for modulo, nombre, valor in ((m.urllib.request, "urlopen", falso),
                                      (m.time, "sleep", lambda s: None)):
            self.addCleanup(setattr, modulo, nombre, getattr(modulo, nombre))
            setattr(modulo, nombre, valor)
        return llamadas

    def _serie(self, respuesta):
        self.addCleanup(setattr, datos, "serie_tvmaze", datos.serie_tvmaze)
        datos.serie_tvmaze = lambda tvid: respuesta

    def _buscar(self, shows):
        self.addCleanup(setattr, m, "pedir", m.pedir)
        m.pedir = lambda *a, **k: None if shows is None else [{"show": s} for s in shows]


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

    def test_un_nombre_con_coma_dentro_no_son_dos_artistas(self):
        # Con los estudios decide el sufijo de empresa, pero "The Creator" no es
        # "Inc.": "Tyler, The Creator" entraba como dos autores y se llevaba dos
        # paginas, "Tyler" y "The Creator", con un disco cada una.
        self.assertEqual(autores.separar("Tyler, The Creator"), ["Tyler, The Creator"])
        # Y sin llevarse por delante lo que si son dos.
        self.assertEqual(autores.separar("Mike Johnson, Tim Burton"),
                         ["Mike Johnson", "Tim Burton"])

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
    def test_un_genero_se_vuelve_tag_en_ascii(self):
        # De cada etiqueta sale una pagina, y de la pagina una direccion: con
        # tilde viaja escapada ("tags/acci%C3%B3n") y el grafo ya no la
        # encuentra. Con las cinco fuentes en ingles no deberia llegar ninguna
        # con acento, pero esta es la ultima puerta antes de escribirla.
        self.assertEqual(datos.etiqueta("  Science Fiction "), "science-fiction")
        self.assertEqual(datos.etiqueta("Acción y Aventura"), "accion-y-aventura")
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
        self.assertEqual(datos.generos_de_subjects(subjects), ["philosophy"])

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
        self.assertEqual(datos.generos_de_subjects(["Fiction, Horror"]), ["horror"])
        self.assertEqual(
            datos.generos_de_subjects(["Fiction / Science Fiction / Hard Science Fiction"]),
            ["science-fiction"])
        self.assertEqual(datos.generos_de_subjects(["Fiction, Mystery & Detective, General"]),
                         ["mystery"])

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
            ["science-fiction"])

    # Los diecinueve generos de Letterboxd, que son lista cerrada y vienen en
    # ingles. Estan aqui y no en el script porque el script ya no los traduce:
    # los escribe tal cual. Son el vocabulario al que tiene que apuntar la tabla
    # de los libros.
    GENEROS_DEL_CINE = {
        "action", "adventure", "animation", "comedy", "crime", "documentary",
        "drama", "family", "fantasy", "history", "horror", "music", "mystery",
        "romance", "science-fiction", "thriller", "tv-movie", "war", "western",
    }

    def test_los_tags_caen_donde_los_de_las_pelis_y_los_juegos(self):
        # De esto vive una pagina de etiqueta: si un libro de terror pusiera
        # `horror` y una peli `terror`, serian dos paginas con una obra cada
        # una en vez de una con las dos. Con las cinco fuentes en ingles se
        # juntan solas, y lo unico que hay que vigilar es esta tabla, que es la
        # unica que sigue eligiendo el nombre del tag.
        destinos = set(datos.GENEROS_OPENLIBRARY.values())
        # Los que no comparte con las pelis son los que el cine no tiene.
        self.assertEqual(sorted(destinos - self.GENEROS_DEL_CINE),
                         ["biography", "philosophy", "poetry"])

    def test_un_libro_sin_coverid_no_pregunta_por_titulo(self):
        # La raya del script: sin el id no hay obra, y buscar "Noches blancas"
        # a ver que sale es justo lo que no hace ninguna de las cinco fuentes.
        def no_llamar(*a, **k):
            self.fail("ha salido a la red sin id")
        original = datos.pedir
        datos.pedir = no_llamar
        self.addCleanup(setattr, datos, "pedir", original)
        valores, detalle = datos.datos_libro("Noches blancas", {}, None)
        self.assertEqual(valores, {})
        self.assertIn("coverid", detalle)


class PorEnlace(unittest.TestCase):
    """El enlace ya lleva el id: de ahi sale el tipo y la obra, sin buscar."""

    def test_cada_enlace_dice_su_tipo_y_su_id(self):
        casos = {
            "https://store.steampowered.com/app/367520/Hollow_Knight/": ("juego", "367520"),
            "https://letterboxd.com/film/heat-1995/": ("peli", "heat-1995"),
            # Abierta desde el diario de otro, con el usuario delante.
            "https://letterboxd.com/alguien/film/parasite-2019/": ("peli", "parasite-2019"),
            "https://www.tvmaze.com/shows/82/game-of-thrones": ("serie", "82"),
            "https://open.spotify.com/intl-es/album/6dVIqQ8qmQ5GBnJ9shOYGE?si=x":
                ("album", "6dVIqQ8qmQ5GBnJ9shOYGE"),
            "https://openlibrary.org/works/OL27448W/The_Lord_of_the_Rings": ("libro", "OL27448W"),
        }
        for enlace, (tipo, ident) in casos.items():
            leido = nueva.leer_enlace(enlace)
            self.assertIsNotNone(leido, enlace)
            self.assertEqual((leido[0], leido[2]), (tipo, ident), enlace)

    def test_una_edicion_sube_a_la_obra_y_no_se_confunde_con_ella(self):
        grupo = "musicbrainz.org/release-group/f5093c06-23e3-404f-aeaa-40f72885ee3a"
        edicion = "musicbrainz.org/release/b84ee12a-09ef-421b-82de-0441a926375b"
        self.assertIs(nueva.leer_enlace(grupo)[1], nueva.album_por_grupo)
        self.assertIs(nueva.leer_enlace(edicion)[1], nueva.album_por_edicion)

    def test_un_titulo_no_es_un_enlace(self):
        self.assertFalse(nueva.es_enlace("hollow knight"))
        self.assertFalse(nueva.es_enlace("peli"))
        self.assertTrue(nueva.es_enlace("boxd.it/2bg8"))
        self.assertIsNone(nueva.leer_enlace("https://example.com/film/x"))

    def test_steam_puede_contestar_con_otra_clave(self):
        # Hollow Knight llego bajo el appid de uno de sus DLC, con el juego
        # dentro. Mirando solo la clave se daba por retirado de la tienda.
        respuesta = {"916000": {"success": True,
                                "data": {"steam_appid": 367520, "name": "Hollow Knight"}}}
        self.assertEqual(m.entrada_steam(respuesta, 367520)["data"]["name"], "Hollow Knight")
        self.assertEqual(m.entrada_steam(respuesta, "999"), {})


class TuTexto(unittest.TestCase):
    """Lo tuyo arriba y lo generado debajo, lo escriba quien lo escriba."""

    CITA = "> [!quote] De qué va\n> Una serie.\n>\n> → Wikipedia · CC BY-SA 4.0\n"

    def test_la_frase_va_encima_de_la_cita_y_la_cita_se_queda(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "Arcane.md"
            md.write_text("---\ntipo: serie\n---\n\n" + self.CITA, encoding="utf-8")
            textos.escribir_lo_suyo(md, "La mejor animación que he visto.")
            texto = md.read_text(encoding="utf-8")
            self.assertLess(texto.index("La mejor"), texto.index("[!quote]"))
            self.assertIn("→ Wikipedia", texto)
            self.assertTrue(texto.startswith("---\ntipo: serie\n---\n"))

    def test_en_una_ficha_vacia_queda_solo_la_frase(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "Baki.md"
            md.write_text("---\ntipo: serie\n---\n", encoding="utf-8")
            textos.escribir_lo_suyo(md, "  Absurda y perfecta.  ")
            self.assertEqual(md.read_text(encoding="utf-8"),
                             "---\ntipo: serie\n---\n\nAbsurda y perfecta.\n")


class LibroPorPortada(unittest.TestCase):
    """De la portada a la obra, y de la obra al articulo: sin buscar por titulo."""

    def test_una_portada_da_su_obra(self):
        respuesta = {"docs": [{"key": "/works/OL1230613W"}]}
        with mock.patch.object(textos, "pedir", return_value=respuesta):
            self.assertEqual(textos.obra_de_portada(13151269), "OL1230613W")

    def test_si_la_portada_sale_en_dos_obras_no_se_elige(self):
        # Antes vacia que con el articulo de otro libro.
        respuesta = {"docs": [{"key": "/works/OL1W"}, {"key": "/works/OL2W"}]}
        with mock.patch.object(textos, "pedir", return_value=respuesta):
            self.assertIsNone(textos.obra_de_portada(1))

    def test_el_campo_wikipedia_manda_y_no_pregunta_a_nadie(self):
        with mock.patch.object(textos, "obra_de_portada") as obra, \
             mock.patch.object(textos, "resumen_wikipedia", return_value="Una novela."):
            cuerpo, _ = textos.texto_libro("x", {"wikipedia": "El extranjero",
                                                 "coverid": "1"}, None)
        obra.assert_not_called()
        self.assertIn("Una novela.", cuerpo)


class Repasar(unittest.TestCase):
    """Una linea por ficha: lo que no se entiende no se escribe a medias."""

    def test_nota_estado_y_favorita_en_cualquier_orden(self):
        self.assertEqual(repasar.interpretar("f 8 t"),
                         {"favorito": True, "nota": 8, "estado": "terminado"})
        self.assertEqual(repasar.interpretar("en curso"), {"estado": "en curso"})
        self.assertEqual(repasar.interpretar("-f"), {"favorito": False})

    def test_una_nota_fuera_de_escala_no_se_escribe(self):
        with self.assertRaises(ValueError):
            repasar.interpretar("11")
        with self.assertRaises(ValueError):
            repasar.interpretar("8 terminao")

    def test_poner_nota_a_lo_pendiente_lo_da_por_terminado(self):
        self.assertEqual(repasar.completar({"estado": ""}, {"nota": 9}),
                         {"nota": 9, "estado": "terminado"})
        self.assertEqual(repasar.completar({"estado": "pendiente"}, {"nota": 9}),
                         {"nota": 9, "estado": "terminado"})

    def test_lo_abandonado_sigue_abandonado_aunque_tenga_nota(self):
        self.assertEqual(repasar.completar({"estado": "abandonado"}, {"nota": 4}),
                         {"nota": 4})
        self.assertEqual(repasar.completar({}, {"nota": 4, "estado": "abandonado"}),
                         {"nota": 4, "estado": "abandonado"})


class Coherencia(unittest.TestCase):
    """Que la vault y lo que los scripts esperan de ella no se separen."""

    def test_cada_seccion_escribe_el_tipo_que_su_base_filtra(self):
        # Si una .base filtra por un tipo que ningun script escribe, la seccion
        # sale vacia en la web sin que falle nada.
        bases = {"juegos": "Juegos", "pelis": "Peliculas", "series": "Series",
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
        for base in ("Peliculas", "Series", "Libros", "Musica"):
            ruta = m.RAIZ / "content" / f"{base}.base"
            if not ruta.exists():
                continue
            texto = ruta.read_text(encoding="utf-8")
            filtrados = set(re.findall(r'note\.estado == "([^"]*)"', texto))
            self.assertTrue(filtrados, f"{base}.base no filtra por estado")
            for estado in filtrados:
                self.assertIn(estado, m.ESTADOS,
                              f'{base}.base filtra por "{estado}", que no existe')

    def test_cada_tipo_tiene_fuente_en_los_cuatro_scripts(self):
        # Una seccion nueva se añade en varios sitios a la vez, y olvidarse de
        # uno no falla: la ficha se crea igual y lo que se queda vacio es la
        # portada, o los tags, o el cuerpo, cada uno por su lado y sin decir por
        # que. Aqui se ve de golpe. `nueva` no entra: sin buscador no hay ni
        # ficha, asi que ese olvido se nota a la primera.
        for tipo in m.SECCIONES.values():
            self.assertIn(tipo, nueva.BUSCADORES, f"{tipo} no se puede dar de alta")
            self.assertIn(tipo, portadas.FUENTES, f"{tipo} no sabe de donde sacar portada")
            self.assertIn(tipo, textos.FUENTES, f"{tipo} no sabe de donde sacar el texto")
        # datos.py es el unico que admite quedarse fuera: hay tipos cuyos campos
        # se ponen todos a mano. Pero si esta, tiene que decir que campos llena.
        for tipo, (fuente, campos) in datos.FUENTES.items():
            self.assertIn(tipo, m.SECCIONES.values(), f"datos.py rellena {tipo}, que no existe")
            self.assertTrue(campos, f"{tipo} no declara que campos rellena")

    def test_las_cinco_secciones_reparten_por_el_mismo_campo(self):
        # Juegos era la excepcion: sus dos ultimas vistas iban por `horas`, que
        # es lo que sabe Steam. Eso ataba la seccion a una sola fuente --un
        # juego apuntado a mano no traia horas y caia en "Por jugar" aunque lo
        # hubieras terminado-- asi que ahora las cinco van por `estado`. Si
        # volviera a quedar un `note.horas` suelto en un .base, la vista
        # filtraria por un campo que ya no escribe nadie: saldria vacia, que es
        # como no estar.
        for base in ("Juegos", "Peliculas", "Series", "Libros", "Musica"):
            texto = (m.RAIZ / "content" / f"{base}.base").read_text(encoding="utf-8")
            self.assertIn('note.estado == "pendiente"', texto, base)
            self.assertNotIn("- note.horas", texto, base)

    def test_ninguna_ficha_guarda_ya_las_horas(self):
        # Las horas siguen decidiendo que entra del volcado de Steam, pero no
        # llegan a la ficha: eran el unico campo que solo sabia rellenar una
        # fuente. Si vuelven a colarse, la cabecera las pintaria otra vez.
        for ficha in (m.RAIZ / "content" / "juegos").glob("*.md"):
            campos = m.frontmatter(ficha.read_text(encoding="utf-8"))
            self.assertIsNone(campos.get("horas"), ficha.name)

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

    def test_los_campos_tuyos_llevan_un_valor_que_las_bases_entienden(self):
        # Son los que se escriben a mano, en Obsidian o con repasar.py, y un
        # valor raro no da error en ningun sitio: "nota: 8,5" o "nota: 9/10"
        # no es un numero y la galeria la ordena al final; "favorito: si" no
        # es true y la ficha no sale en Favoritos. Se ve la web bien, con una
        # obra de menos donde tocaba.
        validos = {"nota": re.compile(r"^(?:[1-9]|10)$"),
                   "year": re.compile(r"^\d{4}$"),
                   "favorito": re.compile(r"^(?:true|false)$"),
                   "draft": re.compile(r"^(?:true|false)$"),
                   "alta": re.compile(r"^\d{4}-\d{2}-\d{2}$")}
        for carpeta in m.SECCIONES:
            for ficha in (m.RAIZ / "content" / carpeta).glob("*.md"):
                if ficha.stem == "index":
                    continue
                campos = m.frontmatter(ficha.read_text(encoding="utf-8"))
                for campo, patron in validos.items():
                    valor = campos.get(campo)
                    if m.vacio(valor):
                        continue
                    self.assertRegex(str(valor), patron,
                                     f"{ficha.name} dice {campo}: {valor}")

    def test_ningun_nombre_de_fichero_se_sale_del_ascii(self):
        # Del nombre del fichero sale la direccion de su pagina, y una tilde o
        # un simbolo ahi viaja escapado: "juegos/dark-souls%E2%84%A2-remastered".
        # El grafo busca la pagina por su nombre, no lo encuentra y la dibuja
        # como un nodo suelto, sin etiquetas y rotulada con la direccion en
        # crudo. Paso de verdad con los tres juegos que llevaban el simbolo de
        # marca registrada y con "El madrileño", y no se ve hasta que abres esa
        # pagina: el titulo de verdad se apunta en `title` y ahi no se nota.
        for carpeta in list(m.SECCIONES) + ["autores"]:
            for ficha in (m.RAIZ / "content" / carpeta).glob("*.md"):
                self.assertTrue(ficha.stem.isascii(),
                                f"{ficha.name} lleva algo que no es ASCII en el nombre")

    def test_ninguna_etiqueta_se_sale_del_ascii(self):
        # Lo mismo, que de cada etiqueta sale tambien una pagina: `acción` daba
        # "tags/acci%C3%B3n" y su grafo salia vacio. Por eso los tags van todos
        # en ingles, que ademas es lo que junta las cinco secciones en la misma
        # etiqueta: `action` es la de los juegos y la de las pelis.
        for carpeta in m.SECCIONES:
            for ficha in (m.RAIZ / "content" / carpeta).glob("*.md"):
                for tag in m.frontmatter(ficha.read_text(encoding="utf-8")).get("tags") or []:
                    self.assertTrue(tag.isascii(),
                                    f"{ficha.name} lleva la etiqueta {tag}")

    def test_un_titulo_con_simbolo_o_tilde_da_un_nombre_de_fichero_ascii(self):
        # Y el simbolo se quita antes de pasar a ASCII: al descomponerlo, "™"
        # se convierte en "TM" y el fichero acababa siendo "DARK SOULSTM".
        self.assertEqual(m.nombre_de_fichero("DARK SOULS™ REMASTERED"),
                         "DARK SOULS REMASTERED")
        self.assertEqual(m.nombre_de_fichero("El madrileño"), "El madrileno")
        self.assertEqual(m.nombre_de_fichero("Idle Slayer – Incremental RPG"),
                         "Idle Slayer - Incremental RPG")

    def test_una_ficha_renombrada_conserva_su_titulo(self):
        # El nombre de fichero pierde el simbolo, pero la ficha no: lo guarda en
        # `title`, que es lo que pinta la web y lo que leen los scripts.
        ficha = m.RAIZ / "content" / "juegos" / "DARK SOULS REMASTERED.md"
        campos = m.frontmatter(ficha.read_text(encoding="utf-8"))
        self.assertEqual(campos.get("title"), "DARK SOULS™ REMASTERED")

    def test_los_generos_de_las_cinco_fuentes_hablan_la_misma_lengua(self):
        # Una etiqueta solo sirve si junta cosas, y para eso los cinco sitios
        # de donde salen tienen que escribirla igual. Si un dia alguien vuelve a
        # traducir una tabla, esto lo dice.
        self.assertEqual(datos.etiqueta("Science Fiction"), "science-fiction")
        self.assertIn("science-fiction", datos.GENEROS_OPENLIBRARY.values())
        for tag in datos.GENEROS_OPENLIBRARY.values():
            self.assertTrue(tag.isascii(), f"la tabla de libros da {tag}")

    def test_cada_ficha_cuelga_de_su_seccion(self):
        # El campo `seccion` es lo unico que une una ficha con su galeria: la
        # galeria es una .base, que no enlaza a nada, asi que sin el la ficha se
        # queda suelta en el grafo de Obsidian y en el de la web. Y como lo
        # escriben los scripts y no se ve en ningun sitio, faltaria en silencio.
        for carpeta in m.SECCIONES:
            debido = m.enlace_seccion(carpeta)
            for ficha in (m.RAIZ / "content" / carpeta).glob("*.md"):
                if ficha.stem == "index":
                    continue
                campos = m.frontmatter(ficha.read_text(encoding="utf-8"))
                self.assertEqual(campos.get("seccion"), debido,
                                 f"{ficha.name} no cuelga de {carpeta}")

    def test_la_seccion_lleva_el_nombre_que_dice_su_indice(self):
        # El rotulo del enlace sale del `title` del index.md, que es donde se
        # escribe una sola vez: si se leyera del nombre de la carpeta, "pelis"
        # saldria asi en vez de "Peliculas".
        self.assertEqual(m.enlace_seccion("pelis"), "[[pelis/index|Películas]]")

    def test_una_ficha_nueva_ya_nace_colgada(self):
        # Asi no hay que pasar secciones.py detras de cada alta.
        with tempfile.TemporaryDirectory() as tmp:
            antes, m.VAULT = m.VAULT, Path(tmp)
            try:
                (m.VAULT / "juegos").mkdir()
                (m.VAULT / "juegos" / "index.md").write_text(
                    "---\ntitle: Juegos\n---\n", encoding="utf-8")
                destino = m.escribir_ficha("juegos", "Celeste", {"tipo": "juego"})
                campos = m.frontmatter(destino.read_text(encoding="utf-8"))
            finally:
                m.VAULT = antes
        self.assertEqual(campos.get("seccion"), "[[juegos/index|Juegos]]")

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
        # El indice no es la pagina de nadie: lo escribe el mismo script para
        # que la carpeta salga titulada "Autores" en el arbol lateral.
        en_disco = ({md.stem for md in carpeta.glob("*.md") if md.stem != "index"}
                    if carpeta.exists() else set())

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
