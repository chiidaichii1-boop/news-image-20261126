# The World, 26 November 2026

[![bounty](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/chiidaichii1-boop/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/chiidaichii1-boop/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

Bounty: https://make.fun/bounty/news-image-20261126

## The image

A newspaper front page summing up Thursday 26 November 2026:

- **Lead:** the US unveils new tariffs on 14 economies — the EU, China, Japan and Taiwan — after an eight-month probe into factory overcapacity.
- **Markets:** stocks slide as an AI sell-off deepens; the S&P 500 and Dow Jones fall into correction territory.
- **Ukraine war:** peace talks stall in Abu Dhabi as Russia holds its territorial claims, while Kyiv hits a Russian air base and two refineries.
- **Energy:** two tankers hit mines and catch fire in the Strait of Hormuz.
- **Nuclear:** North Korea's Kim orders a wider deployment of tactical nuclear weapons.
- **Israel:** judges recommend dropping the most serious charges against Netanyahu.
- **Egypt:** a fuel tanker crash and fire on a Cairo highway kills 30.
- **Thanksgiving:** Macy's postpones its parade and California warns of flooding as king tides peak.

## How it works

`main.py` (Python 3 standard library only) draws the 1024x1024 front page
with a hand-rolled 5x7 bitmap font and a from-scratch PNG encoder, and
writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`, falling back to
`/output/entry.png`. No network, no randomness: two runs produce
byte-identical output.

```sh
python3 main.py
```
