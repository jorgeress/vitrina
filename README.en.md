# Vitrine

*En castellano: [README.md](README.md).*

A personal collection of games, films, series, books and albums, with what you
think of each one. It's written in Obsidian and published as a static website.
This repository is my own, in Spanish
([jorgeress.github.io/vitrina](https://jorgeress.github.io/vitrina/)), and it
works as a template for yours, in English or Spanish.

Each work is a Markdown entry. The site shows each room with its covers and
filters, every entry with your opinion, the best of the best, your groups, a
yearbook and a constellation linking works by what they share. No source needs
an API key, an account or payment.

## Make your own

1. Use this repository as a template on GitHub (or fork it) and clone it.
2. Leave it empty and in English:

   ```bash
   pip install -r requirements.txt
   scripts/empezar.py --language en --name "Shelf" --owner "Alex" \
       --repo https://github.com/alex/shelf --empty --yes
   ```

3. In GitHub, *Settings → Pages → Source*: **GitHub Actions**.
4. Create the Issue labels, to add and edit from your phone:

   ```bash
   gh label create new-piece && gh label create edit-piece
   ```

5. Change the first paragraph of `content/index.md`: it's the site's welcome text.

Every push to `main` runs the tests and publishes the site.

## Run it

You need [Node 22.12+](https://nodejs.org), Python 3 and, to write entries,
[Obsidian](https://obsidian.md).

```bash
pip install -r requirements.txt
cd web
npm ci --ignore-scripts --include=optional
npm run dev            # http://localhost:4321/shelf/
```

- What you save in Obsidian shows up in `npm run dev` right away.
- Without `--ignore-scripts`, `sharp` tries to compile and the install fails.
- Search and share cards are made at build time: `npm run build`, then
  `npm run preview`.

In Obsidian, open **`content/`** as a vault, not the repository root.

### Configuration

`vitrine.config.json`, at the root, is read by the site and the scripts:

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

`language` (`en` or `es`) changes the interface, the page addresses and what the
scripts say. `folders` names each vault folder, which is also each room's
address. `empezar.py` writes it.

Your accounts, to fetch dates (see [When you finished it](#when-you-finished-it)),
go in `vitrine.local.json`, which git ignores:

```json
{ "accounts": { "letterboxd": "user", "steam": "7656119…", "goodreads": "", "listenbrainz": "" } }
```

## Use it

### Adding a work

From its link or searching by title:

```bash
scripts/nueva.py https://store.steampowered.com/app/504230/Celeste/ --rating 9
scripts/nueva.py film "parasite" --rating 10 --favorite
scripts/nueva.py series "death note" --group Anime --finished-on 2021-03
scripts/nueva.py album "in rainbows" --status "in progress"
scripts/nueva.py book "dune" --hidden
```

Links from Steam, Letterboxd, TVmaze, MusicBrainz, Open Library, Spotify, IMDb,
TMDB, MyAnimeList, AniList, Goodreads, Discogs, Wikipedia and more work. The
entry comes with cover, year, author, genres and “What it's about”. The
scripts' names are in Spanish; their messages and options follow `language`.

### From your phone

Open an Issue with the **New piece** form and paste the link; add a rating,
status, groups, date and your opinion if you like. An Action creates the entry,
publishes the site and closes the Issue. It only runs for the owner's Issues.

With the site installed as an app on Android, it shows up in the **Share**
menu: sharing a link from Letterboxd, Steam or Spotify opens the form with the
link in place. It's also at `/add/`.

### Editing from the site

On `/add/`, tick “Show the Edit button”. From then on, in that browser, every
entry has a **✎ Edit** link that opens the **Edit piece** Issue with its current
rating, status, date and opinion. Change what you want, submit it, and it's
published in a couple of minutes.

### Your opinion

What you write goes at the top of the entry, in its own box, with the source's
quote below:

```markdown
> [!vitrine] Why it's on display
> What it left you.
```

No need to write the frame: write loose above the quote and
`scripts/al-dia.py` frames it.

### An entry by hand

A `.md` in its room's folder. Only `type` is required, and keys are always in
English:

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
started_on: 2024-02  # when you started it
times: 2             # how many times you finished it
follows:             # which one it follows; also based_on and soundtrack
  - "[[games/Slay the Spire]]"
---
```

Then run `scripts/al-dia.py`, which adds cover, data and text. The template with
every field explained is `content/_plantillas/Ficha.md`.

### Rating what you already have

```bash
scripts/repasar.py
```

It goes through entries without a rating or status, one line each: `9 f` is a 9
and a favorite, `t` finished, `p` pending, Enter skips, `q` stops. Then it asks
for your opinion.

### Bringing in a collection

```bash
scripts/importar.py letterboxd-rss YOUR_USERNAME
scripts/importar.py steam ~/Downloads/games.html
scripts/importar.py listenbrainz YOUR_USERNAME
scripts/importar.py spotify-export ~/Downloads/spotify.zip
scripts/al-dia.py
```

Imports come in as drafts (`draft: true`): visible in Obsidian, not on the site
until you remove that line. `al-dia.py` fills in what's missing; with
`--offline`, only what needs no network.

### When you finished it

```bash
scripts/cuando.py                          # the accounts in vitrine.local.json
scripts/cuando.py letterboxd YOUR_USERNAME
```

It fills in dates where missing: films from your Letterboxd diary, books from
Goodreads, games from your first Steam achievement, albums from your first
listen on ListenBrainz or in Spotify's history. What isn't certain stays empty.
`al-dia.py` runs it too.

### Groups

Collections across rooms (“Anime”, “What Sam recommended”): `groups: [Anime]`
in the entry. A note with its name in `content/groups/` gives it a text, and
`featured: true` puts it on the home page.

### What shows and what doesn't

| | How | On the site? | On GitHub? |
|---|---|---|---|
| **Draft** | `draft: true` | no | yes |
| **Hidden** | `hidden: true` | no | **yes** |
| **Hidden fields** | `hidden: [rating, opinion]` | the entry yes, those fields no | yes |
| **Private** | in `content/private/` | no | no |

Hidden is not secret: the repository is public. What nobody should see goes in
`content/private/`, which git never uploads. `scripts/vistazo.py` shows the site
with everything in it, on your computer only.

## More (in Spanish)

- [`docs/scripts.md`](docs/scripts.md): every script and its options.
- [`docs/importar.md`](docs/importar.md): what each source brings.
- [`docs/la-web.md`](docs/la-web.md): what each page shows, the vault rules,
  the structure and the tests.

## License

Code under MIT. The texts in `content/` are mine, under CC BY-SA 4.0; in your
vitrine they're yours. Covers belong to their owners and are used as thumbnails
to identify each work. The fonts in `web/fuentes/` are under the SIL Open Font
License. Details in `LICENSE.txt`.
