# GP refine strokes
Blender addon - Bunch of functions for post-drawing strokes refine

**[Download latest](https://github.com/Pullusb/GP_refine_strokes/archive/master.zip)**

<!-- ### [Demo Youtube]() -->

---  

### Where ?
Panel in sidebar : 3D view > sidebar 'N' > Gpencil > Strokes refine (need to be in a GP mode to appear)

## Description

Various tools to affect strokes. Use F9 key to use the _redo_ options when available.  
  
The important things is that almost all the tools act according to the filter you define on top:  

![target_filter](https://github.com/Pullusb/images_repo/raw/master/GPR_strokes_target_filter.png)

This is based on three level : Layer > Frame > Stroke. Be carefull with the targets.  

If you tick `Target last in paint mode`, the target scope is overrided during draw mode and only last stroke is affected.


### Selectors

**Select backward/forward**  
Select strokes from the start or end of the stack in active frame  
![backward select](https://github.com/Pullusb/images_repo/raw/master/gprs_backward_select.gif)

**Select by length**  
Select stroke in active frame that are shorter than given length.  
Hint: you can discard single points (considered 0 length strokes) in the redo panel  
![backward select](https://github.com/Pullusb/images_repo/raw/master/gprs_select_by_length.gif)

**Select by angle**  
F9 to access angle tolerance tweaking via redo panel  
![angle based selection](https://github.com/Pullusb/images_repo/raw/master/GPR_select_by_angle.gif)

**Select hatching**  
Select lines with specific angle. Reference angle can be set with a selected stroke  
![angle based selection](https://github.com/Pullusb/images_repo/raw/master/gprs_hatching_selector.gif)

**Select attribute threshold**  
Select strokes or points if attribute (pressure, opacity) is below or above a given threshold  
All the tweaking and options are available in the F9 redo panel  
![select by attribute](https://github.com/Pullusb/images_repo/raw/master/GPR_select_by_attribute_threshold.gif)

### Stroke refine

**Strokes Delete**  
Delete strokes from the start or end of the stack in active frame  
![backward select](https://github.com/Pullusb/images_repo/raw/master/gprs_backward_delete.gif)

**Trim start/end**  (only work on last stroke)  
each call erase starting/ending point. usefull to adjust when stroke has gone too far  
![Stroke trim](https://github.com/Pullusb/images_repo/raw/master/GPR_trim.gif)
  
**Auto join** (only on last stroke, /!\ experimental, need refining)  
Merge the start of last stroke with nearest stroke tail found  
head cutter tolerance : number (as points) from stroke boundary that are evaluated for the lines merge  
Detection radius : Proximity tolerance to detect surrounding strokes boundaries, relative to screen space, increase if no result  
![auto join](https://github.com/Pullusb/images_repo/raw/master/GPR_autojoin_oval.gif)
  
**straighten**  
Two buttons  
One keep only first and last point so in-between point information like thickness are lost  
The other straighten the point and you can affect influence.
shift+click to reset influence to 100%
ctrl+click for homogen pressure
![straighten](https://github.com/Pullusb/images_repo/raw/master/GPR_straight_influence.gif)
  
**to Circle**
Tranform into average circle
shift+click to reset influence to 100%
ctrl+click for homogen pressure

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

## keymaps

**Alt + X**  
Bind `Strokes Delete` (see upper) to this shortcut
Allow to delete quickly the last bunch of strokes in active layer > frame  
an infinite `Ctrl+Z` ;)

---


## Todo:
- auto-join pressure : make a fade in pressure from chosen old points to new points
- auto-join subdiv : add an intermediate point to avoid a "break" in the line when the auto join
- feature action preference : make an addon preferences to change default options.

<!-- ### Ideas considered : -->
<!-- - feature Context actions : Override scope, default action must affect selection if context mode is edit_stroke (as and option ?) -->

---

Consult [changelog here](CHANGELOG.md)
