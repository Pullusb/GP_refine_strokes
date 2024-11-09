# GP refine strokes

Blender addon - Bunch of functions for Grease Pencil post-drawing strokes adjustment

**[Download latest](https://github.com/Pullusb/GP_refine_strokes/archive/master.zip)**

**[Download for Blender 4.2 and below](https://github.com/Pullusb/GP_refine_strokes/releases/download/v1.2.3/GP_refine_strokes-Blender_4_2-or-below.zip)**

---  

## Where ?

Panel in sidebar : 3D view > sidebar 'N' > Gpencil > Strokes refine (need to be in a GP mode to appear)

## Description

The addon offer various tools to affect strokes.  
Use F9 key to use the _redo_ options when available.  
  
The important things. Almost all the tools respect the filter you define at the top of the panel:  

![target_filter](https://github.com/Pullusb/images_repo/raw/master/GPR_strokes_target_filter.png)


This is based on three level : Layer > Frame > Stroke. Be careful with the targets.  

`Use selection` : Restrict target scope to selected strokes only

`Target last in paint mode` : In draw mode, restrict target scope to last stroke.


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
Select strokes or points if attribute (radius, opacity) is below or above a given threshold  
All the tweaking and options are available in the F9 redo panel  
![select by attribute](https://github.com/Pullusb/images_repo/raw/master/GPR_select_by_attribute_threshold.gif)

### Stroke refine

**Strokes Delete**  
Delete strokes from the start or end of the stack in active frame  
![backward select](https://github.com/Pullusb/images_repo/raw/master/gprs_backward_delete.gif)

**Trim start/end**  (only work on last stroke)  
each call erase starting/ending point. usefull to adjust when stroke has gone too far  
![Stroke trim](https://github.com/Pullusb/images_repo/raw/master/GPR_trim.gif)
  
**straighten**  
Two buttons  
One keep only first and last point so in-between point information like thickness are lost  
The other straighten the point and you can affect influence.  
`Shift + Click` to reset infuence to 100%  
`Ctrl + Click` for homogen radius  
![straighten](https://github.com/Pullusb/images_repo/raw/master/GPR_straight_influence.gif)
  
**to Circle**
Tranform into average circle  
`Shift + Click` to reset infuence to 100%  
`Ctrl + Click` for homogen radius  

**polygonize**  
Like the straighten above but by splitting on angles between point, user can manage angle tolerance.    
![polygonize](https://github.com/Pullusb/images_repo/raw/master/GPR_polygonise.gif)  

### Thickness and opacity

Modify the following strokes attributes:

- Line Width : Pixel radius used when drawing, stored at stroke level
- Line Softness : "Feather" of the stroke defined by used brush when drawing
- Line Fill Alpha : Vertex color used on fill strokes

Modify following points attributes:

- Point Radius : Modulated thickness by Pen radius when drawing, value between `0.0` to `1.0`, can go beyond when changed with radius tool (`Alt+S`)
- Point Opacity : Modulated opacity by Pen pressure, value between `0.0` to `1.0`
- Point Color Alpha : Value to blend between vertex color and stroke material. `0.0` show only material, `1.0` show only painted vertex color.

On all those attributes you can either **add/substract, set or multiply** a value  
![point attribute](https://github.com/Pullusb/images_repo/raw/master/GPR_set-pressure-strength.gif)  

There is also a solution to equalize stroke thickness / pressure

**Equalize stroke thickness**  
![Equalize stroke thickness](https://github.com/Pullusb/images_repo/raw/master/GPR_equalize_stroke_thickness.gif)  

**Equalize point radius**  
![Equalize point radius](https://github.com/Pullusb/images_repo/raw/master/GPR_equalize_point_pressure.gif)  

## Resampling presets

Those are juste shortcuts to native Blender operators (on selection only)  
The resampling operator can be called with some pre-defined value.  
Allow for quick adjustement of stroke's definition.

### Infos

Print stroke/points infos: Display informations in console (according to filter)

## Experimental features

You can enable experimental features in addon preferences
Those are not stable and can easily return errors

**Refine stroke** by progressively fade radius from middle to tip.  
/!\ Works sometimes, percentage is not accurate, can raise errors.
![thin tips](https://github.com/Pullusb/images_repo/raw/master/GPR_thinner_tips.gif)  

**Auto join** (only on last stroke)
/!\ experimental  
Merge the start of last stroke with the nearest stroke tail found  
head cutter tolerance : number (as points) from stroke boundary that are evaluated for the lines merge  
Detection radius : Proximity tolerance to detect surrounding strokes boundaries, relative to screen space, increase if no result  
![auto join](https://github.com/Pullusb/images_repo/raw/master/GPR_autojoin_oval.gif)

## Further notes

Filter management can be tricky at first.

Examples:  
Layer: _Active_, Frame: _Active_, stroke: _Selected_ -> You can select strokes that are on different layer, but here your restricted to 'active layer'.
    
Layer: _All_, Frame: _Active_, stroke: _Last_ -> Here last stroke is not necessarily the one on the active layer (since _All_ layer are targeted)

Keep that in mind when defining your targets

## keymaps

**Alt + X**  
Bind `Strokes Delete` (see upper) to shortcut `Alt + X`  
Allow to delete quickly the last bunch of strokes in active layer > frame  
Like an infinite `Ctrl + Z` !

<!-- 
## Todo:
- auto-join pressure : make a fade in pressure from chosen old points to new points
- auto-join subdiv : add an intermediate point to avoid a "break" in the line when the auto join
- feature action preference : make an addon preferences to change default options.

### Ideas considered :
- feature Context actions : Override scope, default action must affect selection if context mode is edit_stroke (as and option ?)

Gpv3 attributes


##### Strokes
add_points(
aspect_ratio
curve_type
cyclic
end_cap
fill_color
fill_opacity
material_index
points
remove_points(
select
softness
start_cap
time_start


##### Points
delta_time
opacity
position
radius
rotation
select
vertex_color

-->


---

Consult [changelog here](CHANGELOG.md)