bl_info = {
"name": "Gpencil refine strokes",
"description": "Bunch of functions for post drawing strokes refine",
"author": "Samuel Bernou",
"version": (0, 1, 0),
"blender": (2, 80, 0),
"location": "3D view > sidebar 'N' > Gpencil > Strokes refine",
"warning": "",
"wiki_url": "",
"category": "3D View"
}

import bpy
import os
from os import listdir
from os.path import join, dirname, basename, exists, isfile, isdir, splitext
import re, fnmatch, glob
from mathutils import Vector, Matrix
from math import radians, degrees


## addon basic import shortcuts for class types and props
from bpy.props import (IntProperty,
                        StringProperty,
                        BoolProperty,
                        FloatProperty,
                        EnumProperty,
                        CollectionProperty,
                        PointerProperty,
                        IntVectorProperty,
                        BoolVectorProperty,
                        FloatVectorProperty,
                        RemoveProperty,
                        )

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList,
                       AddonPreferences,
                       )

from .utils import *
from .gpfunc import *

### -- OPERATOR --

class GPREFINE_OT_straighten_stroke(Operator):
    bl_idname = "gp.straighten_stroke"
    bl_label = "Straight stroke"
    bl_description = "Make last stroke straight line between first and last point, Influence after in the redo panel"#base on layer/frame/strokes filters
    bl_options = {"REGISTER", "UNDO"}


    influence_val : bpy.props.FloatProperty(name="Straight force", description="Straight interpolation percentage", 
    default=100, min=0, max=100, step=2, precision=1, subtype='PERCENTAGE', unit='NONE')#NONE
    
    def execute(self, context):
        # pref = context.scene.gprsettings
        # L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt
        to_straight_line(get_last_stroke(), keep_points=True, influence = self.influence_val)#, straight_pressure=True
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "influence_val")

    # def invoke(self, context, event):
        
    #     # return {'CANCELLED'}


class GPREFINE_OT_select_by_angle(Operator):
    bl_idname = "gp.select_by_angle"
    bl_label = "Select by angle"
    bl_description = "Select points base on the deviation angle compare to previous and next point (screen space)"#base on layer/frame/strokes filters
    bl_options = {"REGISTER", "UNDO"}

    angle_tolerance : bpy.props.FloatProperty(name="Angle limit", description="Select points by angle of stroke around it", 
    default=40, min=1, max=179, step=2, precision=1, subtype='NONE', unit='NONE')#ANGLE

    reduce : bpy.props.BoolProperty(name="Reduce", description="If multiple points are selected reduce to one by chunck", 
    default=False)
    
    invert : bpy.props.BoolProperty(name="Invert", description="Invert the selection", 
    default=False)
    
    def execute(self, context):
        pref = context.scene.gprsettings
        L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt

        if self.reduce:
            gp_select_by_angle_reducted(self.angle_tolerance, invert=self.invert)
        else:
            gp_select_by_angle(self.angle_tolerance, invert=self.invert)
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "angle_tolerance")
        layout.prop(self, "reduce")
        layout.prop(self, "invert")


class GPREFINE_OT_polygonize(Operator):
    bl_idname = "gp.polygonize_stroke"
    bl_label = "Polygonize"
    bl_description = "Make last stroke straight line between first and last point, Influence after in the redo panel"#base on layer/frame/strokes filters
    bl_options = {"REGISTER", "UNDO"}


    angle_tolerance : bpy.props.FloatProperty(name="Angle limit", description="Turn that have angle above this value (degree) will be considered as polygon corner", 
    default=40, min=0, max=179, step=2, precision=1, subtype='NONE', unit='NONE')#ANGLE

    influence_val : bpy.props.FloatProperty(name="Poygonize force", description="Poygonize interpolation percentage", 
    default=100, min=0, max=100, step=2, precision=1, subtype='PERCENTAGE', unit='NONE')#NONE

    reduce : bpy.props.BoolProperty(name="Reduce", description="Reduce angle chunks to one points", 
    default=False)
    
    def execute(self, context):
        pref = context.scene.gprsettings
        L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt
        gp_polygonize(get_last_stroke(), tol=self.angle_tolerance, influence=self.influence_val, reduce=self.reduce)
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "angle_tolerance")
        layout.prop(self, "influence_val")
        layout.prop(self, "reduce")

    # def invoke(self, context, event):
        
    #     # return {'CANCELLED'}

class GPREFINE_OT_refine_ops(Operator):
    bl_idname = "gp.refine_strokes"
    bl_label = "Refine strokes"
    bl_description = "Refine strokes with multiple different option base on layer/frame/strokes filters"
    bl_options = {"REGISTER", "UNDO"}

    action : StringProperty(name="Action", description="Action to do", default="REFINE", maxlen=0)

    def execute(self, context):
        pref = context.scene.gprsettings
        L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt

        err = None
        ## thinning
        if self.action == "THIN_RELATIVE":
            thin_stroke_tips_percentage(tip_len=pref.percentage_tip_len, variance=pref.percentage_tip_len_random, t_layer=L, t_frame=F, t_stroke=S)
        
        ## -- pressure and strength action
        if self.action == "ADD_PRESSURE":
            gp_add_pressure(amount=pref.add_pressure, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_PRESSURE":
            gp_add_pressure(amount= -pref.add_pressure, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "SET_PRESSURE":
            gp_set_pressure(amount=pref.set_pressure, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SET_STRENGTH":
            gp_set_strength(amount=pref.set_strength, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "ADD_STRENGTH":
            gp_add_strength(amount=pref.set_strength, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_STRENGTH":
            gp_add_strength(amount= -pref.set_strength, t_layer=L, t_frame=F, t_stroke=S)

        ## -- Last stroke modifications

        # trim
        if self.action == "TRIM_START":
            trim_tip_point(endpoint=False)
        
        if self.action == "TRIM_END":
            trim_tip_point()

        if self.action == "GUESS_JOIN":
            err = guess_join(same_material=True, proximity_tolerance=pref.proximity_tolerance, start_point_tolerance=pref.start_point_tolerance)

        if self.action == "STRAIGHT_LAST":
            to_straight_line(get_last_stroke(), keep_points=False, straight_pressure=True)
        
        # if self.action == "POLYGONIZE":
        #     gp_polygonize(pref.poly_angle_tolerance)

        ## -- Infos
        if self.action == "POINTS_INFOS":
            info_pressure(t_layer=L, t_frame=F, t_stroke=S)#t_layer='ACTIVE', t_frame='ACTIVE', t_stroke='SELECT')

        if err is not None:
            self.report({'ERROR'}, err)

        return {"FINISHED"}


### PANELS ----

#generic class attribute and poll for following panels
class GPR_refine:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Gpencil"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.type == 'GPENCIL')

class GPREFINE_PT_stroke_refine_panel(GPR_refine, Panel):
    bl_label = "Strokes refine"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True#send properties to the right side
        # flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        layout.prop(context.scene.gprsettings, 'layer_tgt')
        layout.prop(context.scene.gprsettings, 'frame_tgt')
        layout.prop(context.scene.gprsettings, 'stroke_tgt')
        # row = layout.row(align=False)
        #row = layout.split(align=True,percentage=0.5)
        # row.label(text='arrow choice')

class GPREFINE_PT_thin_tips(GPR_refine, Panel):
    bl_label = "Thin stroke tips"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        # row = layout.row()
        layout.prop(context.scene.gprsettings, 'percentage_use_sync_tip_len')
        layout = self.layout
        if context.scene.gprsettings.percentage_use_sync_tip_len:
            layout.prop(context.scene.gprsettings, 'percentage_tip_len')
        else:
            layout.prop(context.scene.gprsettings, 'percentage_start_tip_len')
            layout.prop(context.scene.gprsettings, 'percentage_end_tip_len')
        layout.prop(context.scene.gprsettings, 'force_max_pressure_line_body')
        layout.operator('gp.refine_strokes').action = 'THIN_RELATIVE'#, icon='GREASEPENCIL'
        layout.label(text="Those settings only affect additive or eraser mode")

class GPREFINE_PT_thickness_opacity(GPR_refine, Panel):
    bl_label = "Thickness and opacity"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        row = layout.row()
        row.prop(context.scene.gprsettings, 'add_pressure')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_PRESSURE'# Sub pressure
        row.operator('gp.refine_strokes', text='+').action = 'ADD_PRESSURE'# Add pressure
        row = layout.row()
        row.prop(context.scene.gprsettings, 'set_pressure')
        row.operator('gp.refine_strokes', text='Set pressure').action = 'SET_PRESSURE'#, icon='GREASEPENCIL'
        row = layout.row()
        row.prop(context.scene.gprsettings, 'set_strength')
        row.operator('gp.refine_strokes', text='Set strength').action = 'SET_STRENGTH'#, icon='GREASEPENCIL'
        row = layout.row()
        row.prop(context.scene.gprsettings, 'add_strength')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_STRENGTH'# Sub strength
        row.operator('gp.refine_strokes', text='+').action = 'ADD_STRENGTH'# Add strength

class GPREFINE_PT_last_stroke_refine(GPR_refine, Panel):
    bl_label = "Last stroke refine"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        row = layout.row()
        row.operator('gp.refine_strokes', text='Trim start', icon='TRACKING_CLEAR_FORWARDS').action = 'TRIM_START'
        row.operator('gp.refine_strokes', text='Trim end', icon='TRACKING_CLEAR_BACKWARDS').action = 'TRIM_END'
        layout.separator()
        layout = self.layout
        layout.prop(context.scene.gprsettings, 'start_point_tolerance')
        layout.prop(context.scene.gprsettings, 'proximity_tolerance')
        layout.operator('gp.refine_strokes', text='Auto join', icon='CON_TRACKTO').action = 'GUESS_JOIN'
        
        row = layout.row()
        row.operator('gp.straighten_stroke', text='Straighten', icon='CURVE_PATH')
        row.operator('gp.refine_strokes', text='Straight strict 2 points', icon='IPO_LINEAR').action = 'STRAIGHT_LAST'
        row = layout.row()
        row.operator('gp.select_by_angle', icon='PARTICLE_POINT')
        row.operator('gp.polygonize_stroke', icon='LINCURVE')
        # row.operator('gp.refine_strokes', text='Polygonize', icon='IPO_CONSTANT').action = 'POLYGONIZE'#generic polygonize
        
        # straigthten line should be a separate operator with influence value... (fully straight lines are boring)
    

class GPREFINE_PT_infos_print(GPR_refine, Panel):
    bl_label = "Infos"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.operator('gp.refine_strokes', text='Print points infos').action = 'POINTS_INFOS'


### -- PROPERTIES --

class GPR_refine_prop(PropertyGroup):
    ## Filters properties
    layer_tgt : EnumProperty(name="Layer target", description="Layer to access", default='ALL',
    items=(
        ('ALL', 'All accessible', 'All layer except hided or locked ones', 0),   
        ('SELECT', 'Selected', 'Only active if selected from layer list, multiple layer can be selected in dopesheet', 1),
        ('ACTIVE', 'Active', 'Only active layer, the one selected in layer list', 2),   
        ('UNRESTRICTED', 'Everything', 'Target all layer of GP object, even hided and locked)', 3),#ghost option ?
        # ('SIDE_SELECT', 'selected without active', 'all the layer selected in dopesheet except active one', 4),   
        )
    )

    frame_tgt : EnumProperty(name="Frame target", description="Frames to access", default='ACTIVE',
    items=(
        ('ACTIVE', 'Active', 'Only active (visible) frame', 0),   
        ('ALL', 'All', 'All frames', 1),   
        ('SELECT', 'Selected', 'Only keyframe selected in dopesheet', 2),
        )
    )

    stroke_tgt : EnumProperty(name="Stroke target", description="Stroke to access", default='SELECT',
    items=(
        ('SELECT', 'Selected', 'Only selected strokes (if at least one point is selected on the stroke it counts as selected)', 0),   
        ('ALL', 'All', 'All Strokes of given layer and frame', 1),   
        ('LAST', 'Last', 'Only last stroke on in frames(s) stroke list', 2),
        )
    )

    ## Tip thinner

    percentage_use_sync_tip_len : BoolProperty(name="Sync tip fade", 
    description="Same tip fade start and end percentage", 
    default=True)

    percentage_tip_len :  IntProperty(name="Tip fade lenght", 
    description="Set the tip fade lenght as a percentage of the strokes points", default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    percentage_tip_len_random :  IntProperty(name="Random", 
    description="Randomize the percentage by this amount around given value\n carefull, with variance each time you relaunch this you alterate the lines", default=0, min=0, max=50, soft_max=25, step=1, subtype='PERCENTAGE')

    percentage_start_tip_len : IntProperty(name="Start tip fade lenght", 
    description="Set the start tip fade lenght as a percentage of the strokes points", default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    percentage_end_tip_len : IntProperty(name="End tip fade lenght", 
    description="Set the end tip fade lenght as a percentage of the strokes points", default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    force_max_pressure_line_body : BoolProperty(name="Force max pressure on line body", 
    description="One the parts that are not fading, put all points pressure to the level of the maximum on the line, fade from this value on tips", 
    default=False)

    ## pressure and strengh handling

    set_pressure : FloatProperty(name="Pressure", description="Points pressure to set (thickness)", 
    default=1.0, min=0, max=5.0, soft_min=0, soft_max=2.0, step=3, precision=2)
    
    add_pressure : FloatProperty(name="Pressure", description="Points pressure to add (thickness)", 
    default=0.02, min=0, max=2.0, soft_min=0, soft_max=1.0, step=3, precision=2)
    
    set_strength : FloatProperty(name="Strength", description="Points strength to set (opacity)", 
    default=1.0, min=0, max=5.0, soft_min=0, soft_max=2.0, step=3, precision=2)

    add_strength : FloatProperty(name="Strength", description="Points strength to add (opacity)", 
    default=0.02, min=0, max=2.0, soft_min=0, soft_max=1.0, step=3, precision=2)
    
    # auto join
    
    proximity_tolerance : FloatProperty(name="Detection radius", description="Proximity tolerance (Relative to view), number of point detected in range printed in console", 
    default=0.01, min=0.00001, max=0.1, soft_min=0.0001, soft_max=0.1, step=3, precision=3)

    start_point_tolerance :  IntProperty(name="Head cutter tolerance", 
    description="Define number of grease pencil point at the start of the last stroke that can be chosen\n0 means only the first point of the stroke is evaluated and the new line will not be cutted",
    default=6, min=0, max=25, soft_max=8, step=1,)

    # polygonize

    poly_angle_tolerance : FloatProperty(name="Angle tolerance", description="Point with corner above this angle will be used as corners", 
    default=45, min=1, max=179, soft_min=5, soft_max=0.1, step=1, precision=1)

### --- REGISTER ---

classes = (
GPR_refine_prop,
GPREFINE_OT_refine_ops,
GPREFINE_OT_straighten_stroke,
GPREFINE_OT_select_by_angle,
GPREFINE_OT_polygonize,
GPREFINE_PT_stroke_refine_panel,#main panel
GPREFINE_PT_last_stroke_refine,
GPREFINE_PT_thickness_opacity,
GPREFINE_PT_thin_tips,
GPREFINE_PT_infos_print,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.gprsettings = PointerProperty(type = GPR_refine_prop)

def unregister():
    del bpy.types.Scene.gprsettings
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
