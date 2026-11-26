# World in One Day — Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Vins1206/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Vins1206/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A make.fun entry for **news-image-20261126** ($100, top 50 share): sum up the world's news of Thursday 26 November 2026 in one image.

## What the image shows

A newspaper front page, drawn entirely in code:

- **Lead story — Oil shock:** Houthis claim a strike on Saudi Arabia's Ras Tanura refinery; Brent crude jumps 3.5% to $94.61 a barrel. Riyadh says it shot down four drones; the claim has not been independently confirmed.
- **Trade — New US tariffs:** Trump proposes duties on 14 partners (China 20%, EU and Japan 15%), with a hearing set for 25 January.
- **Markets — Nvidia on watch:** S&P puts Nvidia on downgrade watch over board fears; AI sell-off hits stocks; Taiwan shares fall 1,927 points.
- **Space:** Pakistan's first astronaut, Muhammad Zeeshan Ali, to fly to China's Tiangong station on Shenzhou-24.
- **USA — Holiday:** the 100th Macy's Thanksgiving Day Parade in New York; US markets closed.
- **Sport — India:** 15-year-old Vaibhav Sooryavanshi hits 204 off 53 balls, a world-record List A double century; India also marks 18 years since 26/11.
- **Also today:** Cairo tanker fire kills 31; Israel strikes in Gaza as the ceasefire strains; Ukraine hits Russian refineries; North Korea expels a Swiss diplomat.

The date — Thursday 26 November 2026 — is named in the masthead, in the date badge, and in the footer.

## How to run

Python 3, standard library only, no network:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024 PNG, under 1 MiB). Two runs produce byte-identical output.

## How it is drawn

`main.py` renders the whole page with a hand-built 5x7 bitmap font and a small PNG encoder written with `zlib`/`struct` — no image libraries, no copied-in image. All news was researched from public sources first, then baked into the program.
