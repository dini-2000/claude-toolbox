# Flags and maps

## Flags
`flags/4x3/<code>.svg` and `flags/1x1/<code>.svg` hold 270 flags in each shape, from flag-icons 7.2.3 by Panayiotis
Lipiridis (MIT, `flags/LICENSE`). The code is the country's ISO 3166-1 two-letter code in lower case: `lk.svg` for Sri
Lanka, `jp.svg` for Japan, `eu.svg` for the European Union. A few more cover regions and groups: `arab` (Arab
League), `cefta`, `eac` (East African Community), `es-ct`, `es-ga`, `es-pv`, `gb-eng`, `gb-nir`, `gb-sct`, `gb-wls`,
`sh-ac`, `sh-hl`, `sh-ta`.

Use a flag as a picture: `<img src="<kit>/assets/flags/4x3/no.svg" alt="Norway">`. The build step
copies it into the finished deck or document, and the PowerPoint converter keeps it as a picture.

- Use `4x3` in rows, tables and legends, and `1x1` for round or square badges (`border-radius: 50%` on the picture).
- Keep every flag in a row at the same height, and give each a thin border in the theme's line colour
  (`border: 1px solid var(--line)`), so a white flag such as Japan's keeps its edge on a light slide.
- Never recolour, stretch or crop a flag beyond the `1x1` set. Use the country's name as the alt text.

## Maps
- `maps/world.svg`: 239 countries and territories in the Equal Earth projection (areas true to size), Antarctica left
  out, 1000 by 449 units.
- `maps/sri-lanka-districts.svg`: the 25 districts. `maps/sri-lanka-provinces.svg`: the 9 provinces. Both use the
  same 560 by 973 frame, so the province map can sit on top of the district map to draw both sets of borders.

Every shape is a `<path>` with data attributes, and no ids, so one map can appear on several slides of a deck:

| Map | Attributes |
|---|---|
| World | `data-iso` (two-letter code in lower case, the flag's file name), `data-iso3`, `data-name`, `data-continent`, `data-label` |
| Sri Lanka | `data-code` (`LK-11` is Colombo District, `LK-1` the Western Province), `data-name`, `data-province` (districts), `data-label` |

`data-label` gives a point inside the shape, in the map's own units, where a label fits. Three world shapes have no
ISO code and use Natural Earth's own: `sol` (Somaliland), `cyn` (Northern Cyprus) and `kas` (Siachen Glacier).

### Using a map
Paste the file's `<svg>` markup into the slide or page, so the theme's colours can reach it (as an `<img>`, a map
shows only its grey default). Give the `<svg>` a class and colour it with the theme's tokens in the deck's `<style>`:

```css
.map { width: 100%; height: auto; display: block }
.map path { fill: var(--surface-2); stroke: var(--bg); stroke-width: .5 }
.map [data-iso="lk"] { fill: var(--accent) }
.map [data-code="LK-1"] { fill: var(--accent) }
```

For values by area (a choropleth), use three to five shades
of one colour, such as `color-mix(in srgb, var(--accent) 35%, var(--bg))`, and put a key on the slide.

- **A region.** Set the pasted map's `viewBox` to the region's box. South Asia is about `viewBox="640 100 130 135"`;
  the `data-label` points of the region's countries show where to draw the box.
- **Labels.** Put labels in HTML over the map: a wrapper with `position: relative` and the map's proportions, and
  each label placed at `left: x / width` and `top: y / height` (in per cent) from its shape's `data-label`. The text
  then stays editable in PowerPoint.
- **Borders.** Keep the land and border colours quiet and let one or two highlights carry the point.

The PowerPoint converter draws a map's shapes as editable shapes in the colours the slide gave them.

### Borders and official use
The maps come from Natural Earth 5.1.2 (public domain): the world map from its 1:50m countries, Sri Lanka from its
1:10m first-level divisions. Natural Earth draws borders as they stand on the ground, which may differ from a
government's official position: Kashmir, Somaliland, Northern Cyprus, Kosovo and Western Sahara among others. Before
a map goes into official work, check the borders it shows with the person, and leave out or merge shapes as they
direct. District and province borders follow Natural Earth too: for a figure that depends on an exact border, use the
national survey office's maps.

## Print profiles
`icc/` holds the colour profiles for print PDFs (see `../README.md`).
