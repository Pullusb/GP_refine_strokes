# GP refine strokes
Blender addon - Bunch of functions for post-drawing strokes refine

**[Download latest](https://github.com/Pullusb/GP_refine_strokes/archive/master.zip)**

<!-- ### [Demo Youtube](https://youtu.be/Rs4y7DeHkp8) -->

---  

## Description

### Where ?
Panel in sidebar : 3D view > sidebar 'N' > Gpencil > Strokes refine

---


## Todo:
- auto-join pressure : make a fade in pressure from chosen old points to new points
- auto-join subdiv : add an intermediate point to avoid a "break" in the line when the auto join
- feature Context actions : Override scope, default action can affect must affect selection if context mode is edit_stroke (as and option ?)
- feature action preference : make an addon preferences to change
- make gifs demos


### Ideas considered :
- Per-layer pseudo color : find a way to "remember" layer with custom color or bypass them (when on AND off)


---

## Changelog:
  2020-03-04 v0.1.2 - :
  - fix set/add stroke
  - added substract stroke option
  - Polygonize can now directly delete intermediate point (yeye !)

  2019-11-03 v0.1.0:
  - New option to toggle visibility and lock object
