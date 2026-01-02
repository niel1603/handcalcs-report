Here’s a **shorter, friendlier, more down-to-earth** version. It avoids sounding grand and makes it clear this is just a practical fork.

---

# handcalcs-report

A small, report-focused fork of [handcalcs](https://github.com/connorferster/handcalcs).

The goal is simple: make calculation notebooks easier to read when you’re writing an actual report, not just doing quick math.

## Why this exists

`handcalcs` is great at turning Python into nice-looking math.
But real engineering or scientific reports usually need more than that:

* Clear section headings
* Short explanations between calculations
* Related equations grouped together
* Fewer notebook cells

This fork adds a lightweight way to structure calculations like a report, while keeping everything you like about `handcalcs`.

We didn’t reinvent anything — just built on top of an already solid project.

## What’s different

* Use `##` lines for **sections, subsections, and notes**
* Put **multiple steps in one cell** instead of many
* Calculations are **grouped automatically**
* Output looks more like a report, less like scratch work
* Fully compatible with existing `handcalcs` options

## Example

Instead of spreading calculations across many cells:

```python
%%render
beam_length = 5.0
```

```python
%%render
w = 10.0
```

You can write one structured cell:

```python
%%render report
## 1. Input

## 1.1. Beam Properties
beam_length = 5.0

## 1.2. Loading
w = 10.0

## 2. Calculation

## 2.1 Bending Moment
The maximum moment occurs at midspan.
M = w * beam_length**2 / 8
```

The output is a clean, readable calculation report with headings, text, and aligned equations.

## How it works (briefly)

Inside a `%%render_report` cell:

* `## 1. Title` → section header
* `## 1.1 Subtitle` → subsection
* `## Some text` → paragraph
* Normal Python lines → rendered equations

That’s it. No extra syntax to learn.

## Status

This is a personal fork made for day-to-day engineering-style reports.
It’s intentionally small and opinionated.

Issues, suggestions, and improvements are welcome.

## Credits

All the heavy lifting comes from the original
[handcalcs](https://github.com/connorferster/handcalcs) by Connor Ferster.
This project just adds a bit of structure on top.

## License

Same license as `handcalcs` (see the original project).

---

If you want, I can also:

* make it even shorter (README-minimal)
* tune the tone to be more “internal tool”
* rewrite it as if it were a quick GitHub fork notice
