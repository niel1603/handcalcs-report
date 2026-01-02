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

Instead of spreading calculations across many cells with separate markdown, you can write structured cell like this:

```python
# import unit
import forallpeople as fp
fp.environment("structural")

m   = fp.m
mm  = fp.mm
kN  = fp.kN
MPa = fp.MPa
GPa = fp.GPa
```

```python
%%render input
# define input

## Load and Resistance Factor Design, LRFD
phi = 0.75

## The angle between the line of action of the required force and the weld longitudinal axis
theta = 0.0

## Fillet weld leg size
# wrapped in parentheses () to skip substitution
Ls = (8.0 * mm) 

## Effective weld length
L = (75.0 * mm) # Comment work like the original

## Filler metal classification strength, E60 → 410 MPa, E70 → 490 MPa
F_EXX = (490 * MPa)

## Number of weld side
N_side = 2
```

```python
%%render report
# define calculation report

## 1. Calculate weld
## 1.1 Calculate weld shear capacity

## Total length of fillet weld
L_total = L * N_side 

## Effective throat thickness
Th = 0.707 * Ls 

## Effective shear area
A_we = Th * L_total

## Design shear stress of weld metal
F_nw = 0.6 * F_EXX 

## Directional strength increase transverse shear
k_ds = (1.0 + 0.5 * (sin(radians(theta)))**1.5)  

## Weld shear capacity
phi_R_n = phi * F_nw * A_we * k_ds
```

The output is a clean, readable calculation report with headings, text, and aligned equations.

## How it works (briefly)

Inside a `%%render report` cell:

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
