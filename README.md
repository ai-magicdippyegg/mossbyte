# Mossbyte 🌱

**A tiny procedural terrarium for your terminal.**

Mossbyte grows a little ecosystem while you watch. Moss spreads, ferns take root, flowers bloom, rain arrives in scattered showers, and the whole miniature world runs from a deterministic random seed.

No frameworks, no dependencies, no network calls. Just Python and a terminal.

## A little preview

```text
MOSSBYTE  /  a tiny living world
+--------------------------------------------------+
|       ,      o                                   |
|    ,  ,,  ,       ,                              |
|  , ,  ,,,      Y       ,                         |
| ,,,,,,, ,,   ,,,,,   ,, ,                         |
|  ,,,,,,,,,,,,,,,,,,,,,,,,,                        |
| ,,,,,,,,,,,,,,,,,,,,,,,,,,,,                      |
|  ,o,,,,,,,,,,,,,,,,,,,,,,,,,,                      |
| ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,                     |
|,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,                    |
+--------------------------------------------------+
 day 028   humidity 61%   moss 184   ferns 12   blooms 4
 seed 2026  |  rain is local, growth is patient
```

*The exact landscape changes with the seed; the preview is illustrative.*

## Run it

Python 3.10 or newer is all you need.

```bash
python mossbyte.py
```

Watch a specific world grow again:

```bash
python mossbyte.py --seed 2026
```

Print a finished landscape without animation:

```bash
python mossbyte.py --steps 80 --static --width 64 --height 20
```

Prefer old-school terminals?

```bash
python mossbyte.py --ascii --plain --seed 42
```

## Options

| Option | Default | What it does |
| --- | ---: | --- |
| `--width` | `48` | World width, from 12 to 120 |
| `--height` | `16` | World height, from 6 to 40 |
| `--steps` | `28` | Number of simulated days |
| `--seed` | random | Repeatable world seed |
| `--delay` | `0.13` | Seconds between animated frames |
| `--static` | off | Print only the final frame |
| `--ascii` | off | Use ASCII instead of Unicode |
| `--plain` | off | Disable terminal colours |

Run `python mossbyte.py --help` for the full help screen.

## The tiny ecosystem

- **Moss** spreads into nearby empty ground when there's enough moisture.
- **Ferns** occasionally emerge from mature moss and can seed new patches.
- **Blooms** appear on established ferns, then settle back into fern growth.
- **Rain** arrives in small local showers; moisture slowly evaporates.
- **Stones** are permanent landmarks.

The simulation uses a seeded pseudo-random generator, so the same size, seed, and number of steps always produce the same world.

## Development

Run the test suite with the Python standard library:

```bash
python -m unittest discover -s tests -t . -v
```

## License

Mossbyte is released under the MIT License. See [LICENSE](LICENSE).
