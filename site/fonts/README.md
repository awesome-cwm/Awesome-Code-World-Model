# Self-hosted fonts

These WOFF2 files ship with the site. There are no runtime font CDN requests.
All families are licensed under SIL Open Font License 1.1; the licenses are
included alongside the files. The subsets cover Latin text. Chinese text uses
the system fallback families defined in `../theme.css`.

| Family | Package | Version | Use |
| --- | --- | --- | --- |
| Newsreader | @fontsource-variable/newsreader | 5.2.8 | Variable upright and italic headings |
| Source Sans 3 | @fontsource-variable/source-sans-3 | 5.2.8 | Variable body text |
| IBM Plex Mono | @fontsource/ibm-plex-mono | 5.2.7 | Regular code and numeric labels |
| VT323 | Google Fonts | Current Latin subset | Embedded display type in `../banner.svg` |

Files were obtained from the pinned packages at `https://cdn.jsdelivr.net/npm/`.
Newsreader and Source Sans 3 license texts include the upstream copyright
notices from `https://github.com/google/fonts/tree/main/ofl/newsreader` and
`https://github.com/google/fonts/tree/main/ofl/sourcesans3`. IBM Plex Mono's
license includes IBM's copyright notice from its pinned package.
VT323 was designed by Peter Hull; its license and standalone Latin subset are
included as `VT323-OFL.txt` and `vt323-latin-regular.woff2`.
