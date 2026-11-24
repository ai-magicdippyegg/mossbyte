"""Mossbyte: a tiny, deterministic terrarium for your terminal."""

from __future__ import annotations

import argparse
import random
import sys
import time
from enum import IntEnum


class Species(IntEnum):
    EMPTY = 0
    MOSS = 1
    FERN = 2
    BLOOM = 3
    STONE = 4


class Terrarium:
    """A small procedural ecosystem driven by a seeded random generator."""

    def __init__(self, width: int = 48, height: int = 16, seed: int = 1) -> None:
        if width < 12 or height < 6:
            raise ValueError("A terrarium must be at least 12 columns by 6 rows.")

        self.width = width
        self.height = height
        self.seed = seed
        self.day = 0
        self._rng = random.Random(seed)
        self.grid = [[Species.EMPTY for _ in range(width)] for _ in range(height)]
        self.age = [[0 for _ in range(width)] for _ in range(height)]
        self.moisture = [
            [
                max(0, min(100, 42 + int(22 * y / max(1, height - 1)) + self._rng.randint(-17, 17)))
                for _ in range(width)
            ]
            for y in range(height)
        ]

        # A soft, irregular moss line gives every new world somewhere to begin.
        for y in range(max(0, height // 2 - 2), height):
            for x in range(width):
                chance = 0.12 + 0.19 * (y / max(1, height - 1))
                if self._rng.random() < chance:
                    self.grid[y][x] = Species.MOSS
                    self.age[y][x] = self._rng.randint(0, 8)

        # A few independent patches make the first frame less uniform.
        for _ in range(max(2, width // 16)):
            cx = self._rng.randrange(width)
            cy = self._rng.randrange(max(1, height // 2))
            self.grid[cy][cx] = Species.MOSS

        # Stones are permanent little landmarks.
        stone_count = max(2, width * height // 110)
        placed = 0
        attempts = 0
        while placed < stone_count and attempts < stone_count * 12:
            attempts += 1
            x = self._rng.randrange(width)
            y = self._rng.randrange(height)
            if self.grid[y][x] == Species.EMPTY:
                self.grid[y][x] = Species.STONE
                placed += 1

    def _neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        return [
            (nx, ny)
            for ny in range(max(0, y - 1), min(self.height, y + 2))
            for nx in range(max(0, x - 1), min(self.width, x + 2))
            if (nx, ny) != (x, y)
        ]

    def step(self) -> None:
        """Advance the ecosystem by one day."""
        next_grid = [row[:] for row in self.grid]
        next_age = [row[:] for row in self.age]
        next_moisture = [row[:] for row in self.moisture]

        for y in range(self.height):
            for x in range(self.width):
                species = self.grid[y][x]
                dampness = self.moisture[y][x]

                # Rain arrives in little local showers; everything slowly dries.
                rain_chance = 0.035 + (y / max(1, self.height - 1)) * 0.035
                rain = self._rng.randint(7, 19) if self._rng.random() < rain_chance else 0
                next_moisture[y][x] = max(0, min(100, dampness - self._rng.randint(0, 3) + rain))
                dampness = next_moisture[y][x]

                if species == Species.STONE or species == Species.EMPTY:
                    continue

                next_age[y][x] += 1
                age = next_age[y][x]

                if species == Species.MOSS:
                    if dampness < 5:
                        next_grid[y][x] = Species.EMPTY
                        next_age[y][x] = 0
                        continue

                    if age >= 8 and dampness >= 45 and self._rng.random() < 0.018:
                        next_grid[y][x] = Species.FERN
                        next_age[y][x] = 0

                    spread_chance = 0.10 + min(dampness, 90) / 500
                    if dampness >= 20 and self._rng.random() < spread_chance:
                        candidates = [
                            (nx, ny)
                            for nx, ny in self._neighbors(x, y)
                            if self.grid[ny][nx] == Species.EMPTY
                            and next_grid[ny][nx] == Species.EMPTY
                        ]
                        if candidates:
                            nx, ny = self._rng.choice(candidates)
                            next_grid[ny][nx] = Species.MOSS
                            next_age[ny][nx] = 0

                elif species == Species.FERN:
                    if dampness < 8:
                        next_grid[y][x] = Species.MOSS
                        next_age[y][x] = 0
                        continue

                    if age >= 7 and dampness >= 42 and self._rng.random() < 0.055:
                        next_grid[y][x] = Species.BLOOM
                        next_age[y][x] = 0

                    if self._rng.random() < 0.075:
                        candidates = [
                            (nx, ny)
                            for nx, ny in self._neighbors(x, y)
                            if self.grid[ny][nx] == Species.EMPTY
                            and next_grid[ny][nx] == Species.EMPTY
                        ]
                        if candidates:
                            nx, ny = self._rng.choice(candidates)
                            next_grid[ny][nx] = Species.MOSS
                            next_age[ny][nx] = 0

                elif species == Species.BLOOM and age >= 7:
                    next_grid[y][x] = Species.FERN
                    next_age[y][x] = 0

        self.grid = next_grid
        self.age = next_age
        self.moisture = next_moisture
        self.day += 1

    def stats(self) -> dict[str, int]:
        counts = {species.name.lower(): 0 for species in Species}
        for row in self.grid:
            for species in row:
                counts[species.name.lower()] += 1
        counts["humidity"] = round(
            sum(sum(row) for row in self.moisture) / (self.width * self.height)
        )
        return counts

    def render(self, *, color: bool = True, ascii_only: bool = False) -> str:
        glyphs = (
            {Species.EMPTY: " ", Species.MOSS: ",", Species.FERN: "Y", Species.BLOOM: "*", Species.STONE: "o"}
            if ascii_only
            else {Species.EMPTY: " ", Species.MOSS: "░", Species.FERN: "♣", Species.BLOOM: "✿", Species.STONE: "●"}
        )
        palette = {
            Species.EMPTY: "\033[90m",
            Species.MOSS: "\033[38;5;71m",
            Species.FERN: "\033[38;5;42m",
            Species.BLOOM: "\033[38;5;211m",
            Species.STONE: "\033[38;5;245m",
        }
        reset = "\033[0m"
        width = self.width + 2
        top = "╭" + "─" * width + "╮" if not ascii_only else "+" + "-" * width + "+"
        bottom = "╰" + "─" * width + "╯" if not ascii_only else "+" + "-" * width + "+"

        lines = [
            "\033[1;32mMOSSBYTE\033[0m  /  a tiny living world" if color else "MOSSBYTE  /  a tiny living world",
            top,
        ]
        for y, row in enumerate(self.grid):
            cells: list[str] = []
            for x, species in enumerate(row):
                glyph = glyphs[species]
                if species == Species.EMPTY and self.moisture[y][x] >= 72:
                    glyph = "~" if ascii_only else "·"
                    cell_color = "\033[38;5;75m"
                else:
                    cell_color = palette[species]
                cells.append(f"{cell_color}{glyph}{reset}" if color and glyph.strip() else glyph)
            lines.append("│ " + "".join(cells) + " │" if not ascii_only else "| " + "".join(cells) + " |")
        lines.append(bottom)

        stats = self.stats()
        summary = (
            f" day {self.day:03d}   humidity {stats['humidity']:02d}%   "
            f"moss {stats['moss']:3d}   ferns {stats['fern']:3d}   "
            f"blooms {stats['bloom']:3d}   stones {stats['stone']:2d}"
        )
        lines.append(summary)
        lines.append(
            f" seed {self.seed}  ·  rain is local, growth is patient"
            if not ascii_only
            else f" seed {self.seed}  |  rain is local, growth is patient"
        )
        return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mossbyte",
        description="Grow a tiny, procedural ecosystem in your terminal.",
        epilog="Tip: use --seed to revisit the exact same little world.",
    )
    parser.add_argument("--width", type=int, default=48, help="world width (12–120; default: 48)")
    parser.add_argument("--height", type=int, default=16, help="world height (6–40; default: 16)")
    parser.add_argument("--steps", type=int, default=28, help="days to simulate (default: 28)")
    parser.add_argument("--seed", type=int, help="random seed for a repeatable world")
    parser.add_argument("--delay", type=float, default=0.13, help="seconds between animated frames (default: 0.13)")
    parser.add_argument("--static", action="store_true", help="skip animation and print only the final world")
    parser.add_argument("--ascii", action="store_true", help="use plain ASCII characters")
    parser.add_argument("--plain", action="store_true", help="disable terminal colours")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not 12 <= args.width <= 120:
        parser.error("--width must be between 12 and 120")
    if not 6 <= args.height <= 40:
        parser.error("--height must be between 6 and 40")
    if not 0 <= args.steps <= 10000:
        parser.error("--steps must be between 0 and 10000")
    if not 0 <= args.delay <= 5:
        parser.error("--delay must be between 0 and 5 seconds")

    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(1_000_000_000)
    garden = Terrarium(args.width, args.height, seed=seed)
    animate = sys.stdout.isatty() and not args.static
    use_color = sys.stdout.isatty() and not args.plain

    if animate:
        for frame in range(args.steps + 1):
            if frame == 0:
                sys.stdout.write("\033[2J")
            sys.stdout.write("\033[H" + garden.render(color=use_color, ascii_only=args.ascii) + "\n")
            sys.stdout.flush()
            if frame < args.steps:
                time.sleep(args.delay)
                garden.step()
    else:
        for _ in range(args.steps):
            garden.step()
        print(garden.render(color=use_color, ascii_only=args.ascii))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
