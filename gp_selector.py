import bpy
# from .utils import *
from . import utils
from . import gpfunc
from mathutils import Vector, Matrix
from math import radians, degrees, copysign, isclose
import numpy as np
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
                    )

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

    @classmethod
    def poll(cls, context):
        return context.object and context.mode in ('EDIT_GPENCIL', 'SCULPT_GPENCIL')
 
    def execute(self, context):
        if context.mode == 'PAINT_GPENCIL':# and pref.use_context:
            return {"CANCELLED"}#disable this one in Paint context

        if self.reduce:
            gpfunc.gp_select_by_angle_reducted(self.angle_tolerance, invert=self.invert)
        else:
            gpfunc.gp_select_by_angle(self.angle_tolerance, invert=self.invert)
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
                s.select = utils.get_stroke_length(s) <= self.length

        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "length")
        layout.prop(self, "include_single_points")

""" 
# standalone func
def hatching_select_on_active_frame():
    ## reference angle to search for
    ref_angle = -53

    ## +/- variation authorized from ref_angle
    tolerance = 20

    # deviation of each segement of the line compared to the next (skipping last)
    # if deviation exceed this angle, skip
    deviation_tolerance = 12

    for s in C.object.data.layers.active.active_frame.strokes:
        count = len(s.points)

        if count < 2:
            continue
        # check deviation
        # view3d_utils.location_3d_to_region_2d(region, rv3d, C.object.matrix_world @ p.co) for p in s.points
        coords_2d = [location_to_region(bpy.context.object.matrix_world @ p.co) for p in s.points]

        
        if count > 2:
            #compare straight level only if at least 3 point
            no_straight = False
            #-2 to evaluate all pts, -3 to avoid last one (often with a coma angle)
            for i in range(len(coords_2d)-3):
                a = coords_2d[i]
                b = coords_2d[i+1]
                c = coords_2d[i+2]
                deviation = abs(degrees((b-a).angle(c-b)))
                if deviation > deviation_tolerance:
                    no_straight = True
                    break
            if no_straight:
                continue
        if count > 3:
            ## on lines with at least four points. do not check the last point (often coma deviated)
            angle = utils.get_ninety_angle_from(coords_2d[0], coords_2d[-2])
        else:
            angle = utils.get_ninety_angle_from(coords_2d[0], coords_2d[-1])
        if not angle:
            continue

        if s.select:
            print('>>', angle)
        if isclose(angle, ref_angle, abs_tol=tolerance):
            s.select = True
 """

def select_if_aligned_to_angle(s, ref_angle, tolerance, non_straight_tol):
    '''
    ref_angle (-45) :: reference angle to search for
    tolerance (20)  :: +/- variation authorized from ref_angle
    non_straight_tol (12) :: Tolerated deviation amount of each segments
    of the line compared to the next (skipping last)
    '''

    count = len(s.points)
    #if not s.select:
    #    continue
    if count < 2:
        return

    # check deviation
    coords_2d = [utils.location_to_region(bpy.context.object.matrix_world @ p.co) for p in s.points]
    
    if count > 2:
        #compare straight level only if at least 3 point
        no_straight = False
        #-2 to evaluate all pts, -3 to avoid last one (often with a coma angle)
        for i in range(len(coords_2d)-3):
            a = coords_2d[i]
            b = coords_2d[i+1]
            c = coords_2d[i+2]
            deviation = abs(degrees((b-a).angle(c-b)))
            #print('deviation:', deviation )
            if deviation > non_straight_tol:
                no_straight = True
                break
        if no_straight:
            return
        
    # if not s.select:
    #     return
    
    if count > 3:
        ## on lines with at least four points. do not check the last point (often coma deviated)
        angle = utils.get_ninety_angle_from(coords_2d[0], coords_2d[-2])
    else:
        angle = utils.get_ninety_angle_from(coords_2d[0], coords_2d[-1])
    if not angle:
        return
    # if s.select:
    #     print('>>', angle)

    ## replace
    # s.select = isclose(angle, ref_angle, abs_tol=tolerance)

    # additive
    if isclose(angle, ref_angle, abs_tol=tolerance):
        #print(angle)
        s.select = True


class GPREFINE_OT_hatching_selector(Operator):
    bl_idname = "gp.hatching_selector"
    bl_label = "Hatching Selector"
    bl_description = "Select straigth strokes based on a -90 to 90 degree angle (0=Horizontal)\ne.g: / = -70, \ = 70, -- = 0"
    bl_options = {"REGISTER", "UNDO"}

    ref_angle: bpy.props.IntProperty(name='Reference Angle', default=-45, 
    description='Reference angle to match from -90 to 90\ne.g: / = -70, \ = 70, -- = 0')

    tolerance: bpy.props.IntProperty(name='Angle Tolerance', default=20, min=0, max=90, 
    description='Consider a matching angle with this amount of variation ')

    non_straight_tol: bpy.props.IntProperty(name='Tolerated deviation', default=12, 
    description='Tolerated deviation amount of each segments\nSkip strokes with segment angle deviating by this amount')

    @classmethod
    def poll(cls, context):
        return context.object and context.mode in ('EDIT_GPENCIL', 'SCULPT_GPENCIL')

    def execute(self, context):
        pref = context.scene.gprsettings
        L, F, S = pref.layer_tgt, pref.frame_tgt, 'ALL'#pref.stroke_tgt
        # if context.mode == 'PAINT_GPENCIL' and pref.use_context:
        #     L, F, S = 'ACTIVE', 'ACTIVE', 'LAST'

        for s in gpfunc.strokelist(t_layer=L, t_frame=F, t_stroke=S):
            select_if_aligned_to_angle(s, self.ref_angle, self.tolerance, self.non_straight_tol)

        return {"FINISHED"}
    
    ## automatic redo panel 
    # def draw(self, context):
    #     layout = self.layout
    #     layout.prop(self, "ref_angle")
    #     layout.prop(self, "tolerance")
    #     layout.prop(self, "non_straight_tol")

class GPREFINE_OT_set_angle_from_stroke(Operator):
    bl_idname = "gp.set_angle_from_stroke"
    bl_label = "Set Ref Angle From Selection"
    bl_description = "Set hatching angle from stroke"
    bl_options = {"REGISTER", "UNDO"}

    ## probably better method : use average angle between segments.
    @classmethod
    def poll(cls, context):
        return context.object and context.mode in ('EDIT_GPENCIL', 'SCULPT_GPENCIL')
    def execute(self, context):
        obj = context.object
        pref = context.scene.gprsettings
        L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt
        if context.mode == 'PAINT_GPENCIL' and pref.use_context:
            L, F, S = 'ACTIVE', 'ACTIVE', 'LAST'

        ## use last selected stroke
        slist = [s for s in gpfunc.strokelist(t_layer=L, t_frame=F, t_stroke=S) if s.select]
        if not slist:
            self.report({'ERROR'}, 'No selected stroke to evaluate')
            return {'CANCELLED'}
        s = slist[-1]
        if len(s.points) < 2:
            self.report({'ERROR'}, 'Stroke have only one point')
            return {'CANCELLED'}
        elif len(s.points) < 5:
            end_id = -1
        else:
            end_id = -2 # avoid some 
        a = utils.location_to_region(obj.matrix_world @ s.points[0].co)
        b = utils.location_to_region(obj.matrix_world @ s.points[end_id].co)
        angle = utils.get_ninety_angle_from(a,b)
        if angle is None:
            self.report({'ERROR'}, f'Could not get angle with a({a}) and b({b}) points')
            return {'CANCELLED'}
        
        context.scene.gprsettings.ref_angle = angle
        self.report({'INFO'}, f'Set {angle:.2f} degree for hatching angle')
        return {"FINISHED"}


## --- backward select


def active_frame_validity_check(context):
    '''return active frame or error message'''
    gpl = context.object.data.layers
    if not gpl.active:
        return 'No active layer'
    if not gpl.active.active_frame:
        return 'No active frame'
    f = gpl.active.active_frame
    if not len(f.strokes):
        return 'No strokes in active layer > frame'
    # return f


class GPREFINE_OT_backward_selector(Operator):
    bl_idname = "gp.backward_selector"
    bl_label = "Backward Selector"
    bl_description = "Select strokes from end to start (On active frame)\nUse slider in redo panel to select a whole slice"
    bl_options = {"REGISTER", "UNDO"}

    backward_select : bpy.props.IntProperty(
    name="Backward Select", description="Number of stroke to select backward", default=1,
    min=1, max=100000, options={'SKIP_SAVE'})

    forward : bpy.props.BoolProperty(name="Forward Select", default=False)
    
    deselect : bpy.props.BoolProperty(name="Deselect", default=False,
        description='Deselect instead of selecting')
    
    replace_selection : bpy.props.BoolProperty(
        name="Replace Selection", default=True,
        description='Replace instead of additive selection\nOnly keep the growing part of the selection/deselection')
    

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'GPENCIL'

    def invoke(self, context, event):
        self.frame = active_frame_validity_check(context)
        if isinstance(self.frame, str):
            self.report({'ERROR'}, self.frame)
            return {"CANCELLED"}

        return self.execute(context)

    def execute(self, context):
        ## prepare list and index
        f = context.object.data.layers.active.active_frame

        self.strokelist = [s for s in f.strokes]
        if not self.forward:
            self.strokelist.reverse()
        
        self.count = len(self.strokelist)
        # find first unselected stroke and keep index
        self.idx = None
        for i, s in enumerate(self.strokelist):
            if not self.deselect and not s.select:
                self.idx = i
                break
            if self.deselect and s.select:
                self.idx = i
                break
        
        if self.idx is None:
            self.report({'WARNING'}, 'Everything is already selected/deselected')
            return {"CANCELLED"}
        
        ## --- evaluation
        self.endex = self.idx+self.backward_select
        if self.endex > self.count:
            self.endex = self.count

        for index in range(self.idx, self.endex):
            # print(f'range {self.idx}-{self.endex} : index {index}')
            self.strokelist[index].select = not self.deselect # True

        if self.replace_selection:
        # skip the current stroke the we just treated and deselect all the other
            for index in range(self.endex+1, self.count):
                # (if endex+1 >= count loop is not entered)
                self.strokelist[index].select = self.deselect # False

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        select_mode = 'Deselect' if self.deselect else 'Select'
        direction = 'Forward' if self.forward else 'Backward'
        icon = 'TRACKING_REFINE_FORWARDS' if self.forward else 'TRACKING_REFINE_BACKWARDS'

        layout.prop(self, "backward_select", text=f'{direction} {select_mode}')
        layout.label(text=f'{self.endex}/{self.count}{" MAX" if self.endex >= self.count else ""}', icon=icon)
        layout.prop(self, "deselect")
        layout.prop(self, "forward")
        layout.prop(self, "replace_selection")


class GPREFINE_OT_backward_stroke_delete(Operator):
    bl_idname = "gp.backward_stroke_delete"
    bl_label = "Backward Stroke Delete"
    bl_description = "Delete strokes from stacks, act as an infinite undo for strokes\nUse slider in redo panel to remove a whole slice"
    bl_options = {"REGISTER", "UNDO"}

    backward_delete : bpy.props.IntProperty(
    name="Delete strokes", description="Number of stroke to select backward", default=1,
    min=1, max=50000, options={'SKIP_SAVE'})

    forward : bpy.props.BoolProperty(name="Forward Delete", default=False) #, options={'SKIP_SAVE'} ? 

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'GPENCIL'

    def invoke(self, context, event):
        self.frame = active_frame_validity_check(context)
        if isinstance(self.frame, str):
            self.report({'ERROR'}, self.frame)
            return {"CANCELLED"}

        return self.execute(context)

    def execute(self, context):
        ## prepare list and index
        f = context.object.data.layers.active.active_frame

        strokelist = [s for s in f.strokes]
        if not self.forward:
            strokelist.reverse()
        
        self.count = len(strokelist)
        
        self.delete_to = self.backward_delete if self.backward_delete < self.count else self.count
        for i, s in enumerate(strokelist[self.delete_to:0:-1]):
            f.strokes.remove(s)

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "backward_delete")
        icon = 'TRACKING_CLEAR_FORWARDS' if self.forward else 'TRACKING_CLEAR_BACKWARDS'
        row.label(text=f'{self.delete_to}/{self.count}{" MAX" if self.backward_delete >= self.count else ""}', icon=icon)
        layout.prop(self, "forward")


class GPREFINE_OT_attribute_selector(Operator):
    bl_idname = "gp.attribute_selector"
    bl_label = "Attribute Threshold Selector"
    bl_description = "Select strokes with a threshold of average points individual attribute (default: pressure)\nTweak settings in redo panel"
    bl_options = {"REGISTER", "UNDO"}

    attr_threshold: bpy.props.FloatProperty(
    name="Attribute threshold", description="Select Strokes/points when pressure is below this threshold", default=0.45,
    min=0.0, max=1.0, step=1, precision=2) #, options={'SKIP_SAVE'}

    attribute: bpy.props.EnumProperty(
        name="Attribute", description="Choose points attribute to use as reference for the selection", 
        default='pressure', #options={'HIDDEN'},
        items=(
            ('pressure', 'Pressure', 'Use point pressure', 0),
            ('strength', 'Strength', 'Use point strength', 1),
            ))
    
    # optional TODO : line width and hardness ? (complicate because not at point level)

    on_points: bpy.props.BoolProperty(name="Individual Points", default=False,
    description='Select individual points instead of strokes')
    
    greater: bpy.props.BoolProperty(name="Greater", default=False,
    description='Select if value is equal or above threshold, else select if value is below')

    method: bpy.props.EnumProperty(
        name="Method", description="Choose method to compares points in strokes with given threshold", 
        default='MEAN', #options={'HIDDEN'},
        items=(
            ('MEAN', 'Mean', 'Use a Mean of all points in each stroke to compare with threshold', 0),
            ('MEDIAN', 'Median', 'Use a Median of all points in each stroke to compare with threshold', 1),
            ('MIN', 'Min', 'Use the minimal point value in each stroke to compare with threshold', 2),
            ('MAX', 'Max', 'Use the maximal point value in each stroke to compare with threshold', 3),
            ))
    
    replace_selection: bpy.props.BoolProperty(
        name="Replace Selection", default=True,
        description='Replace instead of additive selection')
    
    use_target_filter: bpy.props.BoolProperty(
        name="Use Stroke Targets Filter", default=False,
        description='Use GP refine stroke dedicated filter (layer > frame > stroke)\nElse use only active frame of active layer')


    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'GPENCIL'

    def invoke(self, context, event):
        self.frame = active_frame_validity_check(context)
        if isinstance(self.frame, str):
            self.report({'ERROR'}, self.frame)
            return {"CANCELLED"}

        return self.execute(context)

    def execute(self, context):
        ## prepare list and index
        f = context.object.data.layers.active.active_frame
        
        if self.use_target_filter:
            pref = context.scene.gprsettings
            L, F, S = pref.layer_tgt, pref.frame_tgt, pref.stroke_tgt
            strokelist = gpfunc.strokelist(t_layer=L, t_frame=F, t_stroke=S)
        else:
            strokelist = [s for s in f.strokes]

        if self.on_points:
            for s in strokelist:
                for p in s.points:
                    if self.replace_selection:
                        p.select = (getattr(p, self.attribute) < self.attr_threshold) ^ self.greater
                        continue
                    if (getattr(p, self.attribute) < self.attr_threshold) ^ self.greater:
                        p.select = True
            return {"FINISHED"}

        if self.method == 'MEAN': # average
            comp_func = np.mean
        elif self.method == 'MEDIAN':
            comp_func = np.median
        elif self.method == 'MIN':
            comp_func = np.min
        elif self.method == 'MAX':
            comp_func = np.max

        for s in strokelist:
            stroke_pressure = comp_func([getattr(p, self.attribute) for p in s.points])
            if self.replace_selection:
                s.select = (stroke_pressure < self.attr_threshold) ^ self.greater
                continue

            if (stroke_pressure < self.attr_threshold) ^ self.greater:
                s.select = True

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        
        ## Not on same line because redo panel isn't large enough
        layout.label(text='Point' if self.on_points else 'Stroke')

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        row = flow.row()

        if not self.on_points:
            row.prop(self, "method", text='')

        row.prop(self, "attribute", text='')

        compare = '>=' if self.greater else '<'
        row.prop(self, "greater", text=compare, toggle=1)
        # row.label(text=compare)        

        row.prop(self, "attr_threshold", text='')

        ## back to layout
        # flow.prop(self, "greater")
        col = layout.column()
        col.prop(self, "on_points", text='Individual Points')

        # col_method = layout.column()
        # col_method.prop(self, "method")
        # col_method.enabled=not self.on_points
        
        col = layout.column()
        col.prop(self, "use_target_filter")
        col.prop(self, "replace_selection")
        
        #-# Basic 
        # layout.prop(self, "attr_threshold")
        # layout.prop(self, "greater")
        # layout.prop(self, "attribute")
        # layout.prop(self, "method")
        # layout.prop(self, "on_points")
        # layout.prop(self, "replace_selection")

class GPREFINE_OT_coplanar_selector(Operator):
    bl_idname = "gp.coplanar_selector"
    bl_label = "Coplanar Selector"
    bl_description = "Select Non coplanar strokes (On active frame)\nYou can invert in redo panel"
    bl_options = {"REGISTER", "UNDO"}
    
    invert : bpy.props.BoolProperty(name="Invert", default=False,
        description='Select Non Coplanar strokes')
    verbose : bpy.props.BoolProperty(name="Verbose", default=False,
        description='Print information in console')

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'GPENCIL'

    def invoke(self, context, event):
        self.frame = active_frame_validity_check(context)
        if isinstance(self.frame, str):
            self.report({'ERROR'}, self.frame)
            return {"CANCELLED"}

        return self.execute(context)

    def execute(self, context):

        strokes = context.object.data.layers.active.active_frame.strokes
        self.count = len(strokes)
        self.ct = 0
        for s in strokes:
            s.select = gpfunc.is_coplanar_stroke(s, self.verbose) ^ self.invert
            if s.select:
                self.ct +=1

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        target= "non-coplanar" if self.invert else "coplanar"
        layout.label(text=f'{self.ct} {target} selected (/{self.count})')
        layout.prop(self, "invert")
        # layout.prop(self, "verbose")


classes = (
    GPREFINE_OT_select_by_angle,
    GPREFINE_OT_select_by_length,
    GPREFINE_OT_backward_selector,
    GPREFINE_OT_backward_stroke_delete,
    GPREFINE_OT_hatching_selector,
    GPREFINE_OT_set_angle_from_stroke,
    GPREFINE_OT_attribute_selector,
    GPREFINE_OT_coplanar_selector,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


#--- Store ref

""" 
def deselect_more_strokes(from_last=True):
    '''Deselect strokes in order'''
    ## setup error handling
    if not bpy.context.object or bpy.context.object.type != 'GPENCIL':
        print('ERROR','no active object or not GP') 
        return
    
    gpl = bpy.context.object.data.layers

    if not gpl.active:
        print('ERROR','no active layer')
        return
    if not gpl.active.active_frame:
        print('ERROR','no active frame')
        return
    
    f = gpl.active.active_frame
    if not len(f.strokes):
        print('ERROR','no strokes in active layer > frame')
        return
    
    strokelist = [s for s in f.strokes]
    if not from_last:# NOT from last
        strokelist.reverse()
    
    for s in strokelist:
        if s.select:
            s.select = False
            break
"""

'''
def select_more_strokes(from_last=True, clean_after_gap=True):

    ## setup error handling
    if not bpy.context.object or bpy.context.object.type != 'GPENCIL':
        print('ERROR','no active object or not GP') 
        return
    
    gpl = bpy.context.object.data.layers

    if not gpl.active:
        print('ERROR','no active layer')
        return
    if not gpl.active.active_frame:
        print('ERROR','no active frame')
        return
    
    f = gpl.active.active_frame
    total = len(f.strokes)
    if not total:
        print('ERROR','no strokes in active layer > frame')
        return
    
    strokelist = [s for s in f.strokes]
    if from_last:
        strokelist.reverse()
    
    i = 0
    for i, s in enumerate(strokelist):
        if not s.select:
            s.select = True
            break
            
    if not clean_after_gap:
        return

    if i + 1 >= total:# all strokes have been enumerated
        return
    
    i = i+1 # skip the current stroke the we jsut treated
    for index in range(i, total):
        strokelist[index].select = False

select_more_strokes()
'''
