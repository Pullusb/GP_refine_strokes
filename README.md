# GP refine strokes
Blender addon - Bunch of functions for post-drawing strokes refine

**[Download latest](https://github.com/Pullusb/GP_refine_strokes/archive/master.zip)**

<!-- ### [Demo Youtube]() -->

### /!\ WIP : some features are still experimental

---  

### Where ?
Panel in sidebar : 3D view > sidebar 'N' > Gpencil > Strokes refine

## Description

Various tools to affect strokes. use F9 key to use the _redo_ options when available.  
The important things is that most of the tool act according to the scope filter you define on top.  
This is based on three level : Layer > Frame > Stroke. be carefull with the tool target
Also note that a few tools do not use the filter and works only on the last stroke (mosltly)

Tools description:  

**straighten**
Two buttons  
one keep only forst and last point so in-between point information like thickness are lost  
The other straighten keep the point and you can affect influence.

![straighten](https://github.com/Pullusb/images_repo/raw/master/GPR_straight_influence.gif)


**polygonize**  
Like the straighten above but by splitting on angles between point, user can manage angle tolerance.  

![polygonize](https://github.com/Pullusb/images_repo/raw/master/GPR_polygonise.gif)


doc wip...

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
