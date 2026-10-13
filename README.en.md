# Vitrine

*En castellano: [README.md](README.md).*

**Vitrine** is a personal collection — games, films, series, books and albums —
written as Markdown notes in [Obsidian](https://obsidian.md) and published as
a static website. A vitrine is a glass display case: every piece comes with a
label saying why it's there, the way a museum labels what it shows.

This repository is my own, in Spanish (**Vitrina**:
[jorgeress.github.io/vitrina](https://jorgeress.github.io/vitrina/)), but the
tool is meant to be used by anyone, in English or Spanish: one command turns it
into an empty vitrine of your own.

## What it does

- **Rooms** for each kind of work, with covers, search, sorting and filters
  (status, favorites, label, tag) that stay in the address so they can be
  linked.
- **The best of the best**, **groups** you make yourself across rooms
  (“Anime”, “What Sam recommended”), a **yearbook** with what you finished and
  what came in each year, and a **constellation** linking each piece to the
  ones it has most in common with.
- **A share card** for every entry: pasting its link in a chat shows an image
  with the cover, title, rating and the start of your label.
- **Compare** your vitrine with someone else's, by address or with their
  `vitrine.json` file, matching works by their source ids instead of titles.
- **Add a work from its link** (Steam, Letterboxd, TVmaze, MusicBrainz, Open
  Library, Spotify, and through Wikidata IMDb, TMDB, Goodreads, MyAnimeList,
  Discogs and more) with cover, year, author, genres and synopsis.
- **Add from your phone**, with a GitHub Issue form or by sharing a link to the
  installed web app on Android.
- **Import** a Letterboxd diary or watchlist, a Steam library, ListenBrainz or a
  Spotify data export, as drafts to review.
- **Privacy in three levels**: drafts, hidden entries or fields, and a private
  folder that never leaves your computer.
- Installs as an app and works offline; RSS feed and sitemap.
- **No source needs an API key, an account or payment.**

## Make your own

You need [Node 22.12+](https://nodejs.org), Python 3 and Obsidian.

1. Use this repository as a template on GitHub (or fork it) and clone it.
2. Start an empty vitrine in English:

   ```bash
   pip install -r requirements.txt
   scripts/empezar.py --language en --name "Shelf" --owner "Alex" \
       --repo https://github.com/alex/shelf --empty --yes
   ```

   It writes `vitrine.config.json` (the site address comes from the repo:
   `github.com/alex/shelf` → `alex.github.io/shelf`), removes my collection and
   leaves the rooms, the Obsidian views, the home note, the templates and the
   Issue form in English.
3. In GitHub, *Settings → Pages → Source*: **GitHub Actions**. To add from your
   phone, create the Issue label once: `gh label create new-piece`.
4. Open **`content/`** as a vault in Obsidian, and change the first paragraph
   of `content/index.md`: it's the welcome text of the site.

Then, to see it:

```bash
cd web
npm ci --ignore-scripts --include=optional
npm run dev            # http://localhost:4321/shelf/
```

Every push to `main` runs the tests, builds the site and publishes it.

## Configuration: `vitrine.config.json`

```json
{
  "name": "Shelf",
  "owner": "Alex",
  "language": "en",
  "site": "https://alex.github.io",
  "base": "/shelf",
  "repo": "https://github.com/alex/shelf",
  "folders": { "game": "games", "film": "films", "series": "series", "book": "books",
               "album": "music", "author": "authors", "private": "private", "group": "groups" }
}
```

`language` (`en` or `es`) changes the whole interface, the page addresses
(`/authors/`, `/best/`, `/yearbook/`…), what the scripts say, and the language
in which Steam and Wikipedia texts are fetched. `folders` names each vault
folder, which is also the address of each room.

## Adding works

```bash
scripts/nueva.py https://store.steampowered.com/app/504230/Celeste/ --rating 9
scripts/nueva.py film "parasite" --rating 10 --favorite
scripts/nueva.py series "death note" --group Anime --finished-on 2021-03
scripts/nueva.py album "in rainbows" --status "in progress"
scripts/nueva.py book "dune" --hidden
```

With a link there's nothing to choose: it carries the id. Searching by title
shows the candidates and you pick one. The entry comes out complete: cover,
year, author, genres, “What it's about” and the source id. The only thing it
can't write is yours.

**From your phone**: open an Issue with the **New piece** form, paste the link
and, if you like, rating, status, groups, when you finished it, whether it's
among the best, whether it's hidden and why it's on display. An Action creates
the entry, publishes the site and closes the Issue. It only runs for Issues
opened by the repository owner.

**Bringing in a collection**:

```bash
scripts/importar.py letterboxd-rss YOUR_USERNAME
scripts/importar.py letterboxd-watchlist YOUR_USERNAME
scripts/importar.py steam ~/Downloads/games.html
scripts/importar.py listenbrainz YOUR_USERNAME
scripts/importar.py spotify-export ~/Downloads/spotify.zip
scripts/al-dia.py      # fills in covers, data, texts and author pages
```

Imports come in as drafts (`draft: true`): visible in Obsidian, not on the site
until you remove that line. `scripts/repasar.py` goes through entries without
a rating or status and asks, one line each: `9 f` is a 9 and a favorite.

The scripts' names and the code are in Spanish; their messages, options and
`--help` follow `language`. Every option works in both languages (`--rating` or
`--nota`, `film` or `peli`).

## An entry

Keys are always in English, so two vitrines in different languages can be
compared:

```markdown
---
type: game           # game, film, series, book or album
year: 2024
author: LocalThunk
rating: 9            # 1 to 10
status: finished     # pending, in-progress, finished or dropped
favorite: true
tags:
  - strategy
groups:
  - Roguelikes
finished_on: 2024-05 # YYYY, YYYY-MM or YYYY-MM-DD: the yearbook
---

> [!vitrine] Why it's on display
> What it left you.
```

The full template with every field explained is `content/_plantillas/Ficha.md`.

## What shows and what doesn't

| | How | On the site? | On GitHub? |
|---|---|---|---|
| **Draft** | `draft: true` | no | yes |
| **Hidden** | `hidden: true` | no | **yes** |
| **Hidden fields** | `hidden: [rating, label]` | the entry yes, those fields no | yes |
| **Private** | in `content/private/` | no | no |

Hidden is not secret: the repository is public. What nobody should see goes in
`content/private/`, which git never uploads (it has the same room folders and
its own covers). `scripts/vistazo.py` builds the site with everything in it,
marked, on your computer only.

## Structure

```
vitrine.config.json   name, language, address and folders
content/              the vault: the only thing written by hand
scripts/              adding, importing and maintenance (docs/scripts.md, in Spanish)
web/                  the site, in Astro
  src/i18n.ts         every text of the site, in Spanish and English
docs/                 scripts, import sources and the to-do list (in Spanish)
```

## Tests

```bash
python3 scripts/pruebas.py   # offline; also checks no message lacks its translation
cd web && npm test && npm run check
```

## License

Code under MIT. The texts in `content/` are mine, under CC BY-SA 4.0; in your
vitrine they're yours. Covers belong to their owners and are used as thumbnails
to identify each work. The fonts in `web/fuentes/` are under the SIL Open Font
License. Details in `LICENSE.txt`.
