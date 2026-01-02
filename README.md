# handcalcs-report

A small, report-focused fork of [handcalcs](https://github.com/connorferster/handcalcs).

The goal is simple: make calculation notebooks easier to read when you’re writing an actual report, not just doing quick math.

## Why this exists

`handcalcs` does an excellent job of turning Python calculations into clear, readable mathematics. It’s a solid and well-thought-out tool, and this project wouldn’t exist without it.

When working on longer engineering or scientific reports, though, I often found myself wanting a bit more structure around the calculations themselves, such as:

* Clear section headings
* Brief explanations between calculation blocks
* Groups of related equations shown together
* Fewer, more meaningful notebook cells

This fork is a small, report-oriented extension built on top of `handcalcs`. The goal is not to replace or redesign it, but simply to make it a little easier to present calculations in a narrative, report-like form.

## What’s different

* Use `##` lines for **sections, subsections, and notes**
* Allow **multiple calculation steps in a single cell**
* Related calculations are **grouped automatically**
* Output reads more like a report and less like working scratch
* Remains fully compatible with existing `handcalcs` options

## How it works (briefly)

Inside a `%%render report` cell:

* `## 1. Title` → section header
* `## 1.1 Subtitle` → subsection
* `## Some text` → paragraph
* Normal Python lines → rendered equations

That’s it. No extra syntax to learn.

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

## 1. Input

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

## 2. Calculate weld
## 2.1 Calculate weld shear capacity

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

``` markdown
## 1. Input

Load and Resistance Factor Design, LRFD

$
\hspace{2em}\begin{aligned}
\phi &= 0.75 \; 
\end{aligned}
$

The angle between the line of action of the required force and the weld longitudinal axis

$
\hspace{2em}\begin{aligned}
\theta &= 0.00 \; 
\end{aligned}
$

Fillet weld leg size

$
\hspace{2em}\begin{aligned}
\mathrm{Ls} &= 8.00\ \mathrm{mm} \; 
\end{aligned}
$

Effective weld length

$
\hspace{2em}\begin{aligned}
L &= 75.00\ \mathrm{mm} \; \;\textrm{(Comment work like the original)}
\end{aligned}
$

Filler metal classification strength, E60 → 410 MPa, E70 → 490 MPa

$
\hspace{2em}\begin{aligned}
F_{EXX} &= 490.00\ \mathrm{MPa} \; 
\end{aligned}
$

Number of weld side

$
\hspace{2em}\begin{aligned}
N_{side} &= 2 \; 
\end{aligned}
$
```

``` markdown
## 2. Calculate weld

### 2.1 Calculate weld shear capacity

Total length of fillet weld

$$
\begin{aligned}
L_{total} &= L \cdot N_{side} \\&= 75.00\ \mathrm{mm} \cdot 2 \\&= 150.00\ \mathrm{mm}  \\[10pt]
\end{aligned}
$$

Effective throat thickness

$$
\begin{aligned}
\mathrm{Th} &= 0.707 \cdot \mathrm{Ls} \\&= 0.707 \cdot 8.00\ \mathrm{mm} \\&= 5.66\ \mathrm{mm}  \\[10pt]
\end{aligned}
$$

Effective shear area

$$
\begin{aligned}
A_{we} &= \mathrm{Th} \cdot L_{total} \\&= 5.66\ \mathrm{mm} \cdot 150.00\ \mathrm{mm} \\&= 848.40\ \mathrm{mm}^{2}  \\[10pt]
\end{aligned}
$$

Design shear stress of weld metal

$$
\begin{aligned}
F_{nw} &= 0.6 \cdot F_{EXX} \\&= 0.6 \cdot 490.00\ \mathrm{MPa} \\&= 294.00\ \mathrm{MPa}  \\[10pt]
\end{aligned}
$$

Directional strength increase transverse shear

$$
\begin{aligned}
k_{ds} &= \left( 1.0 + 0.5 \cdot \left( \sin \left( \operatorname{radians} \theta \right) \right) ^{ 1.5 } \right) \\&= \left( 1.0 + 0.5 \cdot \left( \sin \left( \operatorname{radians} 0.00 \right) \right) ^{ 1.5 } \right) \\&= 1.00  \\[10pt]
\end{aligned}
$$

Weld shear capacity

$$
\begin{aligned}
\phi R_{n} &= \phi \cdot F_{nw} \cdot A_{we} \cdot k_{ds} \\&= 0.75 \cdot 294.00\ \mathrm{MPa} \cdot 848.40\ \mathrm{mm}^{2} \cdot 1.00 \\&= 187.07\ \mathrm{kN}  \\[10pt]
\end{aligned}
$$
```

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