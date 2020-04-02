# GP refine strokes
Blender addon - Bunch of functions for post-drawing strokes refine

**[Download latest](https://github.com/Pullusb/GP_refine_strokes/archive/master.zip)**

<!-- ### [Demo Youtube]() -->

### /!\ WIP : some features are still experimental

---  

### Where ?
Panel in sidebar : 3D view > sidebar 'N' > Gpencil > Strokes refine (need to be in a GP mode to appear)

## Description

Various tools to affect strokes. Use F9 key to use the _redo_ options when available.  
  
The important things is that most of the tool act according to the  filter you define on top:  

![target_filter](https://github.com/Pullusb/images_repo/raw/master/GPR_strokes_target_filter.png)

This is based on three level : Layer > Frame > Stroke. Be carefull with the targets.  
Also note that a few tools do not use the filter and works directly on the last stroke (mostly).

### Stroke refine

**Trim start/end**  (only work on last stroke)  
each call erase starting/ending point. usefull to adjust when stroke has gone too far  
![Stroke trim](https://github.com/Pullusb/images_repo/raw/master/GPR_trim.gif)
  
**Auto join** (only on last stroke, /!\ experimental, need refining)  
Merge the start of last stroke with nearest stroke tail found  
head cutter tolerance : number (as points) from stroke boundary that are evaluated for the lines merge  
Detection radius : Proximity tolerance to detect surrounding strokes boundarys, relative to screen space, increase if no result  
![auto join](https://github.com/Pullusb/images_repo/raw/master/GPR_autojoin_oval.gif)
  
**straighten**  
Two buttons  
One keep only first and last point so in-between point information like thickness are lost  
The other straighten the point and you can affect influence.
![straighten](https://github.com/Pullusb/images_repo/raw/master/GPR_straight_influence.gif)
  
**select by angle** : F9 to access angle tolerance tweaking
![angle based selection](https://github.com/Pullusb/images_repo/raw/master/GPR_select_by_angle.gif)


**polygonize**  
Like the straighten above but by splitting on angles between point, user can manage angle tolerance.  
![polygonize](https://github.com/Pullusb/images_repo/raw/master/GPR_polygonise.gif)  
  


### Thickness and opacity

Modify the points attributes _pressure_ or _strength_ for targeted strokes (uses filter)  
Can either set it or add/substract by some amount
![point attribute](https://github.com/Pullusb/images_repo/raw/master/GPR_set-pressure-strength.gif)  

  
### Thin stroke tips

**refine stroke** by progressively fade pressure from middle to tip.  
/!\ Works but kind of broken as for now, percentage is not accurate, can raise errors.
![thin tips](https://github.com/Pullusb/images_repo/raw/master/GPR_thinner_tips.gif)  


### Infos

Print points infos: Display list of points pressure in console (according to filter)

### Further notes


Filter management can be tricky sometimes (Need a rework to simplify common operation)  
Examples:  
Layer: _Active_, Frame: _Active_, stroke: _Selected_ -> You can select strokes that are on different layer, but here your restricted to 'active layer'. 
    
Layer: _All_, Frame: _Active_, stroke: _Last_ -> Here last stroke is not necessarily the one on the active layer (since _All_ layer are targeted)

---


## Todo:
- +/- button values strength need fix
- add preset that override filter to work on last stroke or selection. Full filter is sometimes too tricky...
- feature Context actions : Override scope, default action can affect must affect selection if context mode is edit_stroke (as and option ?)
- auto-join pressure : make a fade in pressure from chosen old points to new points
- auto-join subdiv : add an intermediate point to avoid a "break" in the line when the auto join
- feature action preference : make an addon preferences to change default options.

<!-- ### Ideas considered : -->

---

## Changelog:
  2020-04-02 v0.1.4:
  - make props non animatable (used options={'HIDDEN'} value)
  - tweaked layer select mode to prevent potential error
  - line width thickness add/sub and set

  2020-04-01 v0.1.3:
  - addon auto updater in prefs

  2020-03-04 v0.1.2:
  - fix set/add stroke
  - added substract stroke option
  - Polygonize can now directly delete intermediate point (yeye !)

  2019-11-03 v0.1.0:
  - New option to toggle visibility and lock object
