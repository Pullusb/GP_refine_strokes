bl_info = {
"name": "Gpencil refine strokes",
"description": "Bunch of functions for post drawing strokes refine",
"author": "Samuel Bernou",
"version": (0, 4, 2),
"blender": (2, 80, 0),
"location": "3D view > sidebar 'N' > Gpencil > Strokes refine",
"warning": "Wip, some feature are still experimental (auto-join and stroke-fade)",
"doc_url": "https://github.com/Pullusb/GP_refine_strokes",
"category": "3D View"
}

import bpy
import os
from os import listdir
from os.path import join, dirname, basename, exists, isfile, isdir, splitext
import re, fnmatch, glob
from mathutils import Vector, Matrix
from math import radians, degrees

from . import addon_updater_ops# updater

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
from .import gp_keymaps

### -- OPERATOR --

class GPREFINE_OT_straighten_stroke(Operator):
    bl_idname = "gp.straighten_stroke"
    bl_label = "Straight stroke"
    bl_description = "Make stroke a straight line between first and last point, tweak influence in the redo panel\
        \nshift+click to reset infuence to 100%\
        \nctrl+click for equalize thickness"#base on layer/frame/strokes filters
    bl_options = {"REGISTER", "UNDO"}


    influence_val : bpy.props.FloatProperty(name="Straight force", description="Straight interpolation percentage", 
    default=100, min=0, max=100, step=2, precision=1, subtype='PERCENTAGE', unit='NONE')#NONE
    
    homogen_pressure : bpy.props.BoolProperty(name="Equalize pressure", 
    description="Change the pressure of the point (to the mean of all pressure points)", default=False)

    def execute(self, context):
        pref = context.scene.gprsettings
        L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt
        if context.mode == 'PAINT_GPENCIL' and pref.use_context:
            L, F, S = 'ACTIVE', 'ACTIVE', 'LAST'
            #get_last_stroke(context)
        
        for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
            to_straight_line(s, keep_points=True, influence = self.influence_val, straight_pressure = self.homogen_pressure)
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "influence_val")
        layout.prop(self, "homogen_pressure")

    def invoke(self, context, event):
        if context.mode not in ('PAINT_GPENCIL', 'EDIT_GPENCIL'):
            return {"CANCELLED"}
        # self.homogen_pressure = False 
        if event.shift:
            self.influence_val = 100
        self.homogen_pressure = event.ctrl
        # if event.ctrl:
        #     self.homogen_pressure = True
        return self.execute(context)


class GPREFINE_OT_to_circle_shape(Operator):
    bl_idname = "gp.to_circle_shape"
    bl_label = "Shape Circle"
    bl_description = "Round the stroke(s) to a perfect circle, tweak influence in the redo panel\
        \nshift+click to reset infuence to 100%\
        \nctrl+click for equalize thickness"
    bl_options = {"REGISTER", "UNDO"}


    influence_val : bpy.props.FloatProperty(name="Influence", description="Shape shifting interpolation percentage",
    default=100, min=0, max=100, step=2, precision=1, subtype='PERCENTAGE', unit='NONE')#NONE

    homogen_pressure : bpy.props.BoolProperty(name="Equalize Pressure", 
    description="Change the pressure of the point (to the mean of all pressure points)", default=False)
    
    individual_strokes : bpy.props.BoolProperty(name="Individual Strokes", 
    description="Make one circle with all selected point instead of one circle per stroke", default=False)

    def execute(self, context):
        #base on layer/frame/strokes filters -> filter point inside operator
        pref = context.scene.gprsettings
        L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt
        if context.mode == 'PAINT_GPENCIL' and pref.use_context:
            L, F, S = 'ACTIVE', 'ACTIVE', 'LAST'

        if self.individual_strokes or context.mode == 'PAINT_GPENCIL':#all strokes individually
            for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
                to_circle_cast_to_average(context.object, s.points, influence = self.influence_val, straight_pressure = self.homogen_pressure)
        else:
            point_list = []
            for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
                for p in s.points:
                    if p.select:
                        point_list.append(p)
            to_circle_cast_to_average(context.object, point_list, influence = self.influence_val, straight_pressure = self.homogen_pressure)
            

        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "influence_val")
        layout.prop(self, "homogen_pressure")
        if context.mode != 'PAINT_GPENCIL':# Not taken into account in paint (no edits, only last)
            layout.prop(self, "individual_strokes")

    def invoke(self, context, event):
        if context.mode not in ('PAINT_GPENCIL', 'EDIT_GPENCIL'):
            return {"CANCELLED"}
        if event.shift:
            self.influence_val = 100
        self.homogen_pressure = event.ctrl
        # if event.ctrl:
        #     self.homogen_pressure = True
        return self.execute(context)

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
        if context.mode == 'PAINT_GPENCIL':# and pref.use_context:
            return {"CANCELLED"}#disable this one in Paint context

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


class GPREFINE_OT_select_by_length(Operator):
    bl_idname = "gp.select_by_length"
    bl_label = "Select by length"
    bl_description = "Select stroke by 3D length (must be in edit mode)"#base on layer/frame/strokes filters
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object and context.mode in ('EDIT_GPENCIL', 'SCULPT_GPENCIL')

    length : bpy.props.FloatProperty(name="Length", description="Length tolerance", 
    default=0.010, min=0.0, max=1000, step=0.1, precision=4)

    include_single_points : bpy.props.BoolProperty(name='Include single points',
    description="Include single points (0 length) in the selection", default=True)
    
    # self.shift : bpy.props.BoolProperty()

    def invoke(self, context, event):
        self.length = context.scene.gprsettings.length
        self.shift = event.shift
        return self.execute(context)

    def execute(self, context):
        # pref = context.scene.gprsettings
        # L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt
        
        # if not context.mode in ('EDIT_GPENCIL', 'SCULPT_GPENCIL'):# and pref.use_context:
        #     return {"CANCELLED"}#disable this one in Paint context

        ## select stroke based on 3D length
        for l in context.object.data.layers:
            if l.lock or l.hide:
                continue
            for s in l.active_frame.strokes:
                if len(s.points) == 1:
                    s.select = self.include_single_points
                    continue
                s.select = get_stroke_length(s) <= self.length

        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "length")
        layout.prop(self, "include_single_points")

class GPREFINE_OT_polygonize(Operator):
    bl_idname = "gp.polygonize_stroke"
    bl_label = "Polygonize"
    bl_description = "Make last stroke straight line between first and last point, Influence after in the redo panel"#base on layer/frame/strokes filters
    bl_options = {"REGISTER", "UNDO"}


    angle_tolerance : bpy.props.FloatProperty(name="Angle limit", description="Turn that have angle above this value (degree) will be considered as polygon corner", 
    default=40, min=0, max=179, step=2, precision=1, subtype='NONE', unit='NONE')#ANGLE

    influence_val : bpy.props.FloatProperty(name="Polygonize force", description="Poygonize interpolation percentage", 
    default=100, min=0, max=100, step=2, precision=1, subtype='PERCENTAGE', unit='NONE')#NONE

    reduce : bpy.props.BoolProperty(name="Reduce", description="Reduce angle chunks to one points", 
    default=False)

    delete : bpy.props.BoolProperty(name="delete", description="Delete straighten points", 
    default=False)
    
    def execute(self, context):
        pref = context.scene.gprsettings
        L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt
        if context.mode == 'PAINT_GPENCIL' and pref.use_context:
            L, F, S = 'ACTIVE', 'ACTIVE', 'LAST'

        for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
            gp_polygonize(s, tol=self.angle_tolerance, influence=self.influence_val, reduce=self.reduce, delete=self.delete)

        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "angle_tolerance")
        layout.prop(self, "influence_val")
        layout.prop(self, "reduce")
        layout.prop(self, "delete")

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
        if context.mode == 'PAINT_GPENCIL' and pref.use_context:
            L, F, S = 'ACTIVE', 'ACTIVE', 'LAST'

        err = None
        ## thinning
        if self.action == "THIN_RELATIVE":
            thin_stroke_tips_percentage(tip_len=pref.percentage_tip_len, variance=pref.percentage_tip_len_random, t_layer=L, t_frame=F, t_stroke=S)
        
        ## -- pressure and strength action
        if self.action == "ADD_LINE_WIDTH":
            gp_add_line_attr('line_width', amount=pref.add_line_width, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_LINE_WIDTH":
            gp_add_line_attr('line_width', amount= -pref.add_line_width, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "SET_LINE_WIDTH":
            gp_set_line_attr('line_width', amount=pref.set_line_width, t_layer=L, t_frame=F, t_stroke=S) 

        if self.action == "ADD_LINE_HARDNESS":
            gp_add_line_attr('hardness', amount=pref.add_hardness, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_LINE_HARDNESS":
            gp_add_line_attr('hardness', amount= -pref.add_hardness, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "SET_LINE_HARDNESS":
            gp_set_line_attr('hardness', amount=pref.set_hardness, t_layer=L, t_frame=F, t_stroke=S) 

        # Points

        if self.action == "ADD_PRESSURE":
            gp_add_attr('pressure', amount=pref.add_pressure, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_PRESSURE":
            gp_add_attr('pressure', amount= -pref.add_pressure, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "SET_PRESSURE":
            gp_set_attr('pressure', amount=pref.set_pressure, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SET_STRENGTH":
            gp_set_attr('strength', amount=pref.set_strength, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "ADD_STRENGTH":
            gp_add_attr('strength', amount=pref.add_strength, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_STRENGTH":
            gp_add_attr('strength', amount= -pref.add_strength, t_layer=L, t_frame=F, t_stroke=S)

        ## -- Last stroke modifications

        # trim
        if self.action == "TRIM_START":
            # need not only stroke but frame to be able to delete strokes (pass context)
            trim_tip_point(context, endpoint=False)
        
        if self.action == "TRIM_END":
            trim_tip_point(context)

        if self.action == "GUESS_JOIN":
            err = guess_join(same_material=True, proximity_tolerance=pref.proximity_tolerance, start_point_tolerance=pref.start_point_tolerance)

        if self.action == "STRAIGHT_2_POINTS":
            for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
                to_straight_line(s, keep_points=False, straight_pressure=True)
        
        # if self.action == "POLYGONIZE":# own operator for redo panel
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

    # @classmethod
    # def poll(cls, context):
    #     return (context.object is not None and context.object.type == 'GPENCIL')

class GPREFINE_PT_stroke_refine_panel(GPR_refine, Panel):
    bl_label = "Strokes refine"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True#send properties to the right side

        # flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        layout.prop(context.scene.gprsettings, 'layer_tgt')
        layout.prop(context.scene.gprsettings, 'frame_tgt')
        layout.prop(context.scene.gprsettings, 'stroke_tgt')
        layout.prop(context.scene.gprsettings, 'use_context')
        # row = layout.row(align=False)
        #row = layout.split(align=True,percentage=0.5)
        # row.label(text='arrow choice')

class GPREFINE_PT_thin_tips(GPR_refine, Panel):
    bl_label = "Thin stroke tips"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    bl_options = {'DEFAULT_CLOSED'}

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
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        row = layout.row()
        row.prop(context.scene.gprsettings, 'add_line_width')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_LINE_WIDTH'# Sub line_width
        row.operator('gp.refine_strokes', text='+').action = 'ADD_LINE_WIDTH'# Add line_width

        row = layout.row()
        row.prop(context.scene.gprsettings, 'set_line_width')
        row.operator('gp.refine_strokes', text='Set line width').action = 'SET_LINE_WIDTH'

        row = layout.row()
        row.prop(context.scene.gprsettings, 'add_hardness')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_HARDNESS'# Sub line_width
        row.operator('gp.refine_strokes', text='+').action = 'ADD_HARDNESS'# Add line_width

        row = layout.row()
        row.prop(context.scene.gprsettings, 'set_hardness')
        row.operator('gp.refine_strokes', text='Set hardness').action = 'SET_HARDNESS'

        row = layout.row()
        row.prop(context.scene.gprsettings, 'add_pressure')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_PRESSURE'# Sub pressure
        row.operator('gp.refine_strokes', text='+').action = 'ADD_PRESSURE'# Add pressure
        
        row = layout.row()
        row.prop(context.scene.gprsettings, 'set_pressure')
        row.operator('gp.refine_strokes', text='Set pressure').action = 'SET_PRESSURE'#, icon='GREASEPENCIL'
        
        row = layout.row()
        row.prop(context.scene.gprsettings, 'add_strength')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_STRENGTH'# Sub strength
        row.operator('gp.refine_strokes', text='+').action = 'ADD_STRENGTH'# Add strength
        
        row = layout.row()
        row.prop(context.scene.gprsettings, 'set_strength')
        row.operator('gp.refine_strokes', text='Set strength').action = 'SET_STRENGTH'#, icon='GREASEPENCIL'

class GPREFINE_PT_stroke_shape_refine(GPR_refine, Panel):
    bl_label = "Stroke reshape"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        
        ## stroke trimming
        row = layout.row()
        row.operator('gp.refine_strokes', text='Trim start', icon='TRACKING_CLEAR_FORWARDS').action = 'TRIM_START'
        row.operator('gp.refine_strokes', text='Trim end', icon='TRACKING_CLEAR_BACKWARDS').action = 'TRIM_END'
        layout.separator()
        
        ## Shaping
        row = layout.row()
        row.operator('gp.straighten_stroke', text='Straighten', icon='CURVE_PATH')
        row.operator('gp.refine_strokes', text='Straight strict 2 points', icon='IPO_LINEAR').action = 'STRAIGHT_2_POINTS'
        
        row = layout.row()
        row.operator('gp.to_circle_shape', text='To Circle', icon='MESH_CIRCLE')
        
        row = layout.row()
        row.operator('gp.select_by_angle', icon='PARTICLE_POINT')
        row.operator('gp.polygonize_stroke', icon='LINCURVE')

        # layout.separator()
        row = layout.row(align=True)
        row.prop(context.scene.gprsettings, 'length')
        row.operator('gp.select_by_length', text='Select', icon='DRIVER_DISTANCE')
        
        # row.operator('gp.refine_strokes', text='Polygonize', icon='IPO_CONSTANT').action = 'POLYGONIZE'#generic polygonize
        
        layout.separator()
        ## experimental Auto join will come back when fixed
        layout = self.layout
        # layout.label(text='Stroke join')
        layout.prop(context.scene.gprsettings, 'start_point_tolerance')
        layout.prop(context.scene.gprsettings, 'proximity_tolerance')
        layout.operator('gp.refine_strokes', text='Auto join', icon='CON_TRACKTO').action = 'GUESS_JOIN'

        # straigthten line should be a separate operator with influence value... (fully straight lines are boring)
        addon_updater_ops.check_for_update_background()# updater
        addon_updater_ops.update_notice_box_ui(self, context)# updater


class GPREFINE_PT_resampling(GPR_refine, Panel):
    bl_label = "Resampling Presets"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True

        ## resampling preset
        col = layout.column(align=True)
        for i, val in enumerate((0.002, 0.004, 0.006, 0.008, 0.01, 0.015, 0.02, 0.03)):
            if i % 4 == 0:
                row = col.row(align=True)
            row.operator('gpencil.stroke_sample', text = str(val) ).length = val
        layout.operator('gpencil.stroke_simplify').factor = 0.002
        layout.operator('gpencil.stroke_subdivide')

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

    #[‘HIDDEN’, ‘SKIP_SAVE’, ‘ANIMATABLE’, ‘LIBRARY_EDITABLE’, ‘PROPORTIONAL’,’TEXTEDIT_UPDATE’]
    #Bool_variable_name : bpy.props.BoolProperty(name="", description="", default=False, subtype='NONE', options={'ANIMATABLE'}, update=None, get=None, set=None)

    layer_tgt : EnumProperty(name="Layer target", description="Layer to access", default='ALL', options={'HIDDEN'},#SELECT -- ALL allow selection to be okay but kind of conflict with last ...
    items=(
        ('ALL', 'All accessible', 'All layer except hided or locked ones', 0),   
        ('SELECT', 'Selected', 'Only active if selected from layer list, multiple layer can be selected in dopesheet', 1),
        ('ACTIVE', 'Active', 'Only active layer, the one selected in layer list', 2),   
        ('UNRESTRICTED', 'Everything', 'Target all layer of GP object, even hided and locked)', 3),#ghost option ?
        # ('SIDE_SELECT', 'selected without active', 'all the layer selected in dopesheet except active one', 4),   
        )
    )

    frame_tgt : EnumProperty(name="Frame target", description="Frames to access", default='ACTIVE', options={'HIDDEN'},
    items=(
        ('ACTIVE', 'Active', 'Only active (visible) frame', 0),   
        ('ALL', 'All', 'All frames', 1),   
        ('SELECT', 'Selected', 'Only keyframe selected in dopesheet', 2),
        )
    )

    stroke_tgt : EnumProperty(name="Stroke target", description="Stroke to access", default='SELECT', options={'HIDDEN'},#LAST dont work well with ALL layer...
    items=(
        ('SELECT', 'Selected', 'Only selected strokes (if at least one point is selected on the stroke it counts as selected)', 0),   
        ('ALL', 'All', 'All Strokes of given layer and frame', 1),   
        ('LAST', 'Last', 'Only last stroke on in frames(s) stroke list', 2),
        )
    )

    use_context : BoolProperty(name="Target last in paint mode", options={'HIDDEN'},
    description="Change target according to context.\nIn paint mode target last stroke only, (force 'ACTIVE', 'ACTIVE', 'LAST')", 
    default=True)
    ## Tip thinner

    percentage_use_sync_tip_len : BoolProperty(name="Sync tip fade", options={'HIDDEN'},
    description="Same tip fade start and end percentage", 
    default=True)

    percentage_tip_len :  IntProperty(name="Tip fade lenght", options={'HIDDEN'}, 
    description="Set the tip fade lenght as a percentage of the strokes points", default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    percentage_tip_len_random :  IntProperty(name="Random", options={'HIDDEN'}, 
    description="Randomize the percentage by this amount around given value\n carefull, with variance each time you relaunch this you alterate the lines", default=0, min=0, max=50, soft_max=25, step=1, subtype='PERCENTAGE')

    percentage_start_tip_len : IntProperty(name="Start tip fade lenght", options={'HIDDEN'}, 
    description="Set the start tip fade lenght as a percentage of the strokes points", default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    percentage_end_tip_len : IntProperty(name="End tip fade lenght", options={'HIDDEN'}, 
    description="Set the end tip fade lenght as a percentage of the strokes points", default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    force_max_pressure_line_body : BoolProperty(name="Force max pressure on line body", options={'HIDDEN'}, 
    description="One the parts that are not fading, put all points pressure to the level of the maximum on the line, fade from this value on tips", 
    default=False)

    ### Line and points attributes

    # width (brush radius)
    set_line_width : IntProperty(name="line width", description="Line width to set (correspond to brush radius, pixel value)", options={'HIDDEN'}, 
    default=10, min=0, max=500, soft_min=0, soft_max=150)

    add_line_width : IntProperty(name="line width", description="Line width radius to add (correspond to brush radius, pixel value)", options={'HIDDEN'}, 
    default=1, min=0, max=300, soft_min=0, soft_max=100)

    # hardness (opacity gradient from border to middle of the line)
    set_hardness : FloatProperty(name="Hardness", description="Hardness to set\nAmount of transparency to apply from the border of the point to the center.\nWorks only when the brush is using stroke materials of Dot or Box style", 
    default=1.0, min=0, max=1.0, soft_min=0, soft_max=1.0, precision=2, options={'HIDDEN'})

    add_hardness : FloatProperty(name="Hardness", description="Hardness radius to add\nAmount of transparency to apply from the border of the point to the center.\nWorks only when the brush is using stroke materials of Dot or Box style", 
    default=0.1, min=0, max=1.0, soft_min=0, soft_max=1.0, precision=2, options={'HIDDEN'})

    # pressure (pen pressure)
    set_pressure : FloatProperty(name="Pressure", description="Points pressure to set (thickness)", options={'HIDDEN'}, 
    default=1.0, min=0, max=5.0, soft_min=0, soft_max=2.0, step=3, precision=2)
    
    add_pressure : FloatProperty(name="Pressure", description="Points pressure to add (thickness)", options={'HIDDEN'}, 
    default=0.1, min=0, max=2.0, soft_min=0, soft_max=1.0, step=3, precision=2)
    
    # strength (opacity)
    set_strength : FloatProperty(name="Strength", description="Points strength to set (opacity)", options={'HIDDEN'}, 
    default=1.0, min=0, max=5.0, soft_min=0, soft_max=2.0, step=3, precision=2)

    add_strength : FloatProperty(name="Strength", description="Points strength to add (opacity)", options={'HIDDEN'}, 
    default=0.1, min=0, max=2.0, soft_min=0, soft_max=1.0, step=3, precision=2)
    
    # auto join
    
    proximity_tolerance : FloatProperty(name="Detection radius", description="Proximity tolerance (Relative to view), number of point detected in range printed in console", options={'HIDDEN'}, 
    default=0.01, min=0.00001, max=0.1, soft_min=0.0001, soft_max=0.1, step=3, precision=3)

    start_point_tolerance :  IntProperty(name="Head cutter tolerance", options={'HIDDEN'}, 
    description="Define number of grease pencil point at the start of the last stroke that can be chosen\n0 means only the first point of the stroke is evaluated and the new line will not be cutted",
    default=6, min=0, max=25, soft_max=8, step=1,)

    # polygonize

    poly_angle_tolerance : FloatProperty(name="Angle tolerance", description="Point with corner above this angle will be used as corners", options={'HIDDEN'}, 
    default=45, min=1, max=179, soft_min=5, soft_max=0.1, step=1, precision=1)


    # length tolerance
    length : bpy.props.FloatProperty(name="Length", description="Length tolerance", 
    default=0.010, min=0.0, max=1000, step=0.1, precision=4, options={'HIDDEN'})



## updater
class GPR_addonprefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    auto_check_update : bpy.props.BoolProperty(
    name="Auto-check for Update",
    description="If enabled, auto-check for updates using an interval",
    default=False,
    )

    updater_intrval_months : bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days : bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
        )
    updater_intrval_hours : bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes : bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )

    def draw(self, context):
        layout = self.layout
        addon_updater_ops.update_settings_ui(self, context)

### --- REGISTER ---

classes = (
GPR_addonprefs,# updater
GPR_refine_prop,
GPREFINE_OT_refine_ops,
GPREFINE_OT_straighten_stroke,
GPREFINE_OT_to_circle_shape,
GPREFINE_OT_select_by_angle,
GPREFINE_OT_polygonize,
GPREFINE_OT_select_by_length,
GPREFINE_PT_stroke_refine_panel,#main panel
GPREFINE_PT_stroke_shape_refine,
GPREFINE_PT_thickness_opacity,
GPREFINE_PT_resampling,
GPREFINE_PT_thin_tips,
# GPREFINE_PT_infos_print,
gp_keymaps.GPREFINE_OT_delete_last_stroke,
)


def register():
    addon_updater_ops.register(bl_info)# updater
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    gp_keymaps.register()#keymaps
    bpy.types.Scene.gprsettings = PointerProperty(type = GPR_refine_prop)

def unregister():
    addon_updater_ops.unregister()# updater
    del bpy.types.Scene.gprsettings
    gp_keymaps.unregister()#keymaps
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
