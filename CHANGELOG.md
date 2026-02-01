# Changelog

2.2.0 - 2026-02-01

- changed: replaced `Use selection` and `Use last in paint mode` by a single `Target Filter` checkbox to enable the triple filter
- changed: More compact UI. Target scope is now part of a sub-panel, all panel and subpanels are closed by default


2.1.1 - 2026-01-10

- added: option to change the minimum thickness in experimental tool `Tip thinner`

2.1.0 - 2025-12-15

- added: Fill alpha subpanel to affect separately fill_color's alpha and fill opacity

2.0.0 - 2024-11-09

- changed: Addon is fully converted to GPv3 for blender 4.3+ (breaking retro-compatibility) :
- removed: incompatible features with GPv3 (ex: resample stroke presets, since preset used native operator)
- removed: some operator option that neededed too much rework (often when `drawing` and `stroke index` is needed where function only reived a `stroke` object)

1.2.3 - 2023-02-18

- removed: Equalizer unused `Affect Strokes Individually`

1.2.2 - 2023-02-16

- fixed: hatching selector, set angle from selection error

1.2.1 - 2023-02-12

- changed: move attribute harmonizer panel ops to related thickness and opacity subpanels
- added: addon preferences with Experimental checkbox, display unstable/beta tools

1.2.0 - 2023-02-11

- added: Thickness and opacity multiply attribute operations
- changed: UI subpanels for thickness and opacity tweaks

1.1.0 - 2023-02-11

- added: attribute harmonizer (beta)

1.0.0 - 2022-06-06

- added: methods to modulate stroke `Fill Alpha` in `Thickness & Opacity`

0.9.0 - 2022-06-01

- changed: make select by length work according to scope
- removed: obsolete updater

0.8.0 - 2022-01-17

- feat: batch tweak GP point vertex color

0.7.1 - 2021-09-14

- feat: coplanarity selector (on active frame)

0.7.0 - 2021-06-14

- feat: add context select mode to set target on selection by default.
- feat: add analyse panel with functions to console print infos on strokes, points and pressure.
- ui: triple filter is now greyed out if overrided

0.6.1 - 2021-05-12

- fix : hardness add/sub/set
- code: add changelog file


0.6.0 - 2021-03-06

- feat: new select by attribute threshold (value and multiple options in redo panel)
- ui: added auto-join strokes in a dedicated subpanel (this feature is still experimental and was confounded with the rest)
- code: little cleaning

0.5.0 - 2021-02-22

- UI: sort by actions, added a `Selections` category dedicated to these operations
- feat: backward/forward select/deselect with options in redo panel
- feat: Stroke deleter (binded on shortcut `alt+X`)
- feat: hatching selector
- Code refactor

0.4.3 - 2021-02-07

- code: Added secondary stroke eraser shortcut code disabled (commented, not ready yet)
- fix: updater verbose mode to False

0.4.2 - 2020-11-14

- changed default simplify value to `0.002`

0.4.1 - 2020-10-31

- fix: auto-join bug

0.4.0 - 2020-10-10

- Feat: to Circle operator with options influence, thickness equalization and individual stroke
- add flatten pressure for straight stroke with influence tweaking
- some code correction

0.3.0 - 2020-10-02

- feat: select by stroke length
- UI: remove property split for upper panel (more readable)

0.2.0 - 2020-06-20

- feature : New tickbox to make paint context override filters to target last stroke only for majority of operations
- feature : added control of hardness
- fix : corrected add/sub strength
- code : refactor of strokes/points tweaking functions (now use get/set attr)

0.1.6 - 2020-04-11

- Keymap: Added alt + X shortcut in GP Draw mode to delete last stroke (Hack to use when Ctrl+Z is too slow because of too heavy scene)
<!-- - removed Auto-join and fade feature... -->

0.1.5 - 2020-04-06

- Critical: Fix mistake in layer selection filter when retrieving stroke list to affect.

0.1.4 - 2020-04-02

- make props non animatable (used options={'HIDDEN'} value)
- tweaked layer select mode to prevent potential error
- line width thickness add/sub and set

0.1.3 - 2020-04-01

- addon auto updater in prefs

0.1.2 - 2020-03-04

- fix set/add stroke
- added substract stroke option
- Polygonize can now directly delete intermediate point (yeye !)

0.1.0 - 2019-11-03

- New option to toggle visibility and lock object
