bl_info = {
"name": "Gpencil refine strokes",
"description": "Bunch of functions for post drawing strokes refining",
"author": "Samuel Bernou",
"version": (1, 2, 1),
"blender": (3, 3, 0),
"location": "3D view > sidebar 'N' > Gpencil > Strokes refine",
"warning": "",
"doc_url": "https://github.com/Pullusb/GP_refine_strokes",
"tracker_url": "https://github.com/Pullusb/GP_refine_strokes/issues",
"category": "3D View"
}

import bpy

from . import preferences
from . import gp_selector
from . import gp_harmonizer
from . import ui


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


    influence_val : bpy.props.FloatProperty(name="Straight force",
        description="Straight interpolation percentage", 
        default=100, min=0, max=100, step=2, precision=1,
        subtype='PERCENTAGE', unit='NONE')
    
    homogen_pressure : bpy.props.BoolProperty(name="Equalize pressure", 
        description="Change the pressure of the points (average pressure)",
        default=False)

    def execute(self, context):
        pref = context.scene.gprsettings
        L, F, S = get_context_scope(context)

        for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
            to_straight_line(s,
                             keep_points=True,
                             influence = self.influence_val,
                             straight_pressure = self.homogen_pressure)
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


    influence_val : bpy.props.FloatProperty(name="Influence", 
        description="Shape shifting interpolation percentage",
        default=100, min=0, max=100, step=2, precision=1, 
        subtype='PERCENTAGE', unit='NONE')#NONE

    homogen_pressure : bpy.props.BoolProperty(name="Equalize Pressure", 
        description="Change the pressure of the points (average pressure)", 
        default=False)
    
    individual_strokes : bpy.props.BoolProperty(name="Individual Strokes", 
        description="Make one circle with all selected point\
            \ninstead of one circle per stroke", 
        default=False)

    def execute(self, context):
        #base on layer/frame/strokes filters -> filter point inside operator
        pref = context.scene.gprsettings
        L, F, S = get_context_scope(context)

        if self.individual_strokes or context.mode == 'PAINT_GPENCIL':#all strokes individually
            for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
                to_circle_cast_to_average(context.object, s.points,
                    influence=self.influence_val,
                    straight_pressure=self.homogen_pressure)
        else:
            point_list = []
            for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
                for p in s.points:
                    if p.select:
                        point_list.append(p)
            to_circle_cast_to_average(context.object, point_list,
                influence=self.influence_val,
                straight_pressure=self.homogen_pressure)

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

class GPREFINE_OT_polygonize(Operator):
    bl_idname = "gp.polygonize_stroke"
    bl_label = "Polygonize"
    bl_description = "Poligonize the line Influence after in the redo panel\
        \nBases on layer/frame/strokes filters"
    bl_options = {"REGISTER", "UNDO"}


    angle_tolerance : bpy.props.FloatProperty(name="Angle limit", 
        description="Angles above this value (degree) are considered polygon corner", 
        default=40, min=0, max=179, step=2, precision=1,
        subtype='NONE', unit='NONE') # ANGLE

    influence_val : bpy.props.FloatProperty(name="Polygonize force",
        description="Poygonize interpolation percentage", 
        default=100, min=0, max=100, step=2, precision=1, 
        subtype='PERCENTAGE', unit='NONE') # NONE

    reduce : bpy.props.BoolProperty(name="Reduce", 
        description="Reduce angle chunks to one points", 
        default=False)

    delete : bpy.props.BoolProperty(name="delete",
        description="Delete straighten points", 
        default=False)
    
    def execute(self, context):
        L, F, S = get_context_scope(context)

        for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
            gp_polygonize(s,
                          tol=self.angle_tolerance,
                          influence=self.influence_val,
                          reduce=self.reduce,
                          delete=self.delete)

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
    bl_description = "Refine strokes with multiple different option\
        \nbase on layer/frame/strokes filters"
    bl_options = {"REGISTER", "UNDO"}

    action : StringProperty(name="Action", 
                            description="Action to do", 
                            default="REFINE", maxlen=0)

    def invoke(self, context, event):
        self.shift = event.shift
        return self.execute(context)

    def execute(self, context):
        pref = context.scene.gprsettings
        L, F, S = get_context_scope(context)

        err = None
        ## thinning
        if self.action == "THIN_RELATIVE":
            thin_stroke_tips_percentage(tip_len=pref.percentage_tip_len, 
                                        variance=pref.percentage_tip_len_random, 
                                        t_layer=L, t_frame=F, t_stroke=S)
        
        ## -- pressure and strength action
        if self.action == "ADD_LINE_WIDTH":
            gp_add_line_attr('line_width', amount=pref.add_line_width, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_LINE_WIDTH":
            gp_add_line_attr('line_width', amount= -pref.add_line_width, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "SET_LINE_WIDTH":
            gp_set_line_attr('line_width', amount=pref.set_line_width, t_layer=L, t_frame=F, t_stroke=S) 

        if self.action == "MULT_LINE_WIDTH":
            gp_mult_line_attr('line_width', amount=pref.mult_line_width, t_layer=L, t_frame=F, t_stroke=S) 

        if self.action == "ADD_LINE_HARDNESS":
            gp_add_line_attr('hardness', amount=pref.add_hardness, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_LINE_HARDNESS":
            gp_add_line_attr('hardness', amount= -pref.add_hardness, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "SET_LINE_HARDNESS":
            gp_set_line_attr('hardness', amount=pref.set_hardness, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "MULT_LINE_HARDNESS":
            gp_mult_line_attr('line_width', amount=pref.mult_line_hardness, t_layer=L, t_frame=F, t_stroke=S)

        ## -- Points

        if self.action == "ADD_PRESSURE":
            gp_add_attr('pressure', amount=pref.add_pressure, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_PRESSURE":
            gp_add_attr('pressure', amount= -pref.add_pressure, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "SET_PRESSURE":
            gp_set_attr('pressure', amount=pref.set_pressure, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "MULT_PRESSURE":
            gp_mult_attr('pressure', amount=pref.mult_pressure, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "ADD_STRENGTH":
            gp_add_attr('strength', amount=pref.add_strength, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SUB_STRENGTH":
            gp_add_attr('strength', amount= -pref.add_strength, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "SET_STRENGTH":
            gp_set_attr('strength', amount=pref.set_strength, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "MULT_STRENGTH":
            gp_mult_attr('strength', amount=pref.mult_strength, t_layer=L, t_frame=F, t_stroke=S)
        
        # - vertex color
        if self.action == "SET_ALPHA":
            gp_set_vg_alpha(amount=pref.set_alpha, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "ADD_ALPHA":
            gp_add_vg_alpha(amount=pref.add_alpha, t_layer=L, t_frame=F, t_stroke=S)
    
        if self.action == "SUB_ALPHA":
            gp_add_vg_alpha(amount= -pref.add_alpha, t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "MULT_ALPHA":
            gp_mult_vg_alpha(amount= pref.mult_alpha, t_layer=L, t_frame=F, t_stroke=S)

        # stroke color fill
        if self.action == "SET_FILL_ALPHA":
            gp_set_stroke_vg_col_fill_alpha(amount=pref.set_fill_alpha, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "ADD_FILL_ALPHA":
            gp_add_stroke_vg_col_fill_alpha(amount=pref.add_fill_alpha, t_layer=L, t_frame=F, t_stroke=S)
    
        if self.action == "SUB_FILL_ALPHA":
            gp_add_stroke_vg_col_fill_alpha(amount= -pref.add_fill_alpha, t_layer=L, t_frame=F, t_stroke=S)

        if self.action == "MULT_FILL_ALPHA":
            gp_mult_stroke_vg_col_fill_alpha(amount= pref.mult_fill_alpha, t_layer=L, t_frame=F, t_stroke=S)

        ## -- Last stroke modifications

        # trim
        if self.action == "TRIM_START":
            # need not only stroke but frame to be able to delete strokes (pass context)
            trim_tip_point(context, endpoint=False)
        
        if self.action == "TRIM_END":
            trim_tip_point(context)

        if self.action == "GUESS_JOIN":
            err = guess_join(same_material=True,
                             proximity_tolerance=pref.proximity_tolerance,
                             start_point_tolerance=pref.start_point_tolerance)

        if self.action == "STRAIGHT_2_POINTS":
            for s in strokelist(t_layer=L, t_frame=F, t_stroke=S):
                to_straight_line(s, keep_points=False, straight_pressure=True)
        
        # if self.action == "POLYGONIZE":# own operator for redo panel
        #     gp_polygonize(pref.poly_angle_tolerance)

        ## -- Infos
        if self.action == "INSPECT_STROKES":
            inspect_strokes(t_layer=L, t_frame=F, t_stroke=S)
        
        if self.action == "INSPECT_POINTS":
            inspect_points(t_layer=L, t_frame=F, t_stroke=S, all_infos=self.shift)
        
        if self.action == "POINTS_PRESSURE_INFOS":
            info_pressure(t_layer=L, t_frame=F, t_stroke=S)

        if err is not None:
            self.report({'ERROR'}, err)

        return {"FINISHED"}


### -- PROPERTIES --

class GPR_refine_prop(PropertyGroup):
    ## Filters properties

    # [‘HIDDEN’, ‘SKIP_SAVE’, ‘ANIMATABLE’, ‘LIBRARY_EDITABLE’, ‘PROPORTIONAL’,’TEXTEDIT_UPDATE’]
    # Bool_variable_name : bpy.props.BoolProperty(name="", description="", 
    # default=False, subtype='NONE', options={'ANIMATABLE'}, update=None, get=None, set=None)

    # SELECT -- ALL allow selection to be okay but kind of conflict with last ...
    layer_tgt : EnumProperty(name="Layer target",
        description="Layer to access", 
        default='ALL', options={'HIDDEN'},
        items=(
            ('ALL', 'All accessible', 'All layer except hided or locked ones', 0),   
            ('SELECT', 'Selected', 'Only active if selected from layer list, multiple layer can be selected in dopesheet', 1),
            ('ACTIVE', 'Active', 'Only active layer, the one selected in layer list', 2),   
            ('UNRESTRICTED', 'Everything', 'Target all layer of GP object, even hided and locked)', 3), #ghost option ?
            # ('SIDE_SELECT', 'selected without active', 'all the layer selected in dopesheet except active one', 4),   
            )
        )

    frame_tgt : EnumProperty(name="Frame target", 
        description="Frames to access", default='ACTIVE', options={'HIDDEN'},
        items=(
            ('ACTIVE', 'Active', 'Only active (visible) frame', 0),   
            ('ALL', 'All', 'All frames', 1),   
            ('SELECT', 'Selected', 'Only keyframe selected in dopesheet', 2),
            )
        )

    # LAST dont work well with ALL layer...
    stroke_tgt : EnumProperty(name="Stroke target",
        description="Stroke to access", default='SELECT', options={'HIDDEN'},
        items=(
            ('SELECT', 'Selected', 'Only selected strokes (if one point selected, stroke counts as selected)', 0),   
            ('ALL', 'All', 'All Strokes of given layer and frame', 1),   
            ('LAST', 'Last', 'Only last stroke on in frames(s) stroke list', 2),
            )
        )

    use_context : BoolProperty(name="Use last in paint mode", options={'HIDDEN'},
        description="Change target according to context.\
            \nIn paint mode target last stroke only, (force 'ACTIVE', 'ACTIVE', 'LAST')", 
        default=True)
    
    use_select : BoolProperty(name="Use Selection", options={'HIDDEN'},
        description="Use only context selection as target in edit and sculpt mode\
            \n(force 'ALL', 'ACTIVE', 'SELECT')", 
        default=True)
    
    ## Tip thinner
    percentage_use_sync_tip_len : BoolProperty(name="Sync tip fade", options={'HIDDEN'},
        description="Same tip fade start and end percentage", 
        default=True)

    percentage_tip_len :  IntProperty(name="Tip fade lenght", options={'HIDDEN'}, 
        description="Set the tip fade lenght as a percentage of the strokes points",
        default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    percentage_tip_len_random :  IntProperty(name="Random", options={'HIDDEN'}, 
        description="Randomize the percentage by this amount around given value\
        \nCarefull, with variance each time you relaunch this you alterate the lines", 
        default=0, min=0, max=50, soft_max=25, step=1, subtype='PERCENTAGE')

    percentage_start_tip_len : IntProperty(name="Start tip fade lenght", options={'HIDDEN'}, 
        description="Set the start tip fade lenght as a percentage of the strokes points", 
        default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    percentage_end_tip_len : IntProperty(name="End tip fade lenght", options={'HIDDEN'}, 
        description="Set the end tip fade lenght as a percentage of the strokes points", 
        default=20, min=5, max=100, step=1, subtype='PERCENTAGE')
    
    force_max_pressure_line_body : BoolProperty(name="Force max pressure on line body",                              
        description="On the parts that are not fading, set pressure to maximum level of the line\
            \nFade from this value on tips", 
        default=False, options={'HIDDEN'},)

    ### Line and points attributes


    # width (brush radius)
    set_line_width : IntProperty(name="Line Width",
        description="Line width to set (brush radius, pixel value)",
        default=10, min=0, max=500, soft_min=0, soft_max=150, options={'HIDDEN'})

    add_line_width : IntProperty(name="Line Width",
        description="Line width radius to add (brush radius, pixel value)",
        default=1, min=0, max=300, soft_min=0, soft_max=100, options={'HIDDEN'})

    mult_line_width : FloatProperty(name="Line Width",
        description="Line width radius to multiply (brush radius, multiply pixel value)", 
        default=0.9, min=0, max=4.0, soft_max=2.0, precision=2, options={'HIDDEN'})

    # hardness (opacity gradient from border to middle of the line)
    set_hardness : FloatProperty(name="Hardness", 
        description="Hardness to set\
            \nAmount of transparency to apply from the border of the point to the center.\
            \nWorks only when the brush is using stroke materials of Dot or Box style", 
        default=1.0, min=0, max=1.0, soft_min=0, soft_max=1.0, precision=2, options={'HIDDEN'})

    add_hardness : FloatProperty(name="Hardness", 
        description="Hardness radius to add\
            \nAmount of transparency to apply from the border of the point to the center.\
            \nWorks only when the brush is using stroke materials of Dot or Box style", 
        default=0.1, min=0, max=1.0, soft_min=0, soft_max=1.0, precision=2, options={'HIDDEN'})

    mult_line_hardness : FloatProperty(name="Hardness", 
        description="Hardness radius to Multiply\
            \nMultiply transparency to apply from the border of the point to the center.\
            \nWorks only when the brush is using stroke materials of Dot or Box style", 
        default=0.9, min=0, max=4.0, soft_max=2.0, precision=2, options={'HIDDEN'})

    # pressure (pen pressure)
    set_pressure : FloatProperty(name="Pressure",
        description="Points pressure to set (thickness)", options={'HIDDEN'}, 
        default=1.0, min=0, max=5.0, soft_min=0, soft_max=2.0, step=3, precision=2)
    
    add_pressure : FloatProperty(name="Pressure",
        description="Points pressure to add (thickness)", options={'HIDDEN'}, 
        default=0.1, min=0, max=2.0, soft_min=0, soft_max=1.0, step=3, precision=2)

    mult_pressure : FloatProperty(name="Pressure",
        description="Multiply points pressure by value", 
        default=0.9, min=0, max=4.0, soft_max=2.0, precision=2, options={'HIDDEN'})

    # strength (opacity)
    set_strength : FloatProperty(name="Strength",
        description="Points strength to set (opacity)", options={'HIDDEN'}, 
        default=1.0, min=0, max=5.0, soft_min=0, soft_max=2.0, step=3, precision=2)

    add_strength : FloatProperty(name="Strength",
        description="Points strength to add (opacity)", options={'HIDDEN'}, 
        default=0.1, min=0, max=2.0, soft_min=0, soft_max=1.0, step=3, precision=2)

    mult_strength : FloatProperty(name="Strength",
        description="Multiply points strength by value (opacity)", 
        default=0.9, min=0, max=4.0, soft_max=2.0, precision=2, options={'HIDDEN'})

    # alpha (point color opacity)
    set_alpha : FloatProperty(name="Vertex Alpha",
        description="Vertex color alpha to set (point color opacity)", options={'HIDDEN'}, 
        default=0.0, min=0, max=1.0, step=3, precision=2)

    add_alpha : FloatProperty(name="Vertex Alpha",
        description="Vertex color alpha to add (point color opacity)", options={'HIDDEN'}, 
        default=0.1, min=0, max=1.0, soft_min=0, soft_max=1.0, step=3, precision=2)

    mult_alpha : FloatProperty(name="Vertex Alpha",
        description="Multiply vertex color alpha (point color opacity)", 
        default=0.9, min=0, max=4.0, soft_max=2.0, precision=2, options={'HIDDEN'})

    # fill alpha (stroke fill color opacity)
    set_fill_alpha : FloatProperty(name="Fill Alpha",
        description="Vertex fill color alpha to set (stroke color opacity)", options={'HIDDEN'}, 
        default=0.0, min=0, max=1.0, step=3, precision=2)

    add_fill_alpha : FloatProperty(name="Fill Alpha",
        description="Vertex fill color alpha to add (stroke color opacity)", options={'HIDDEN'}, 
        default=0.1, min=0, max=1.0, soft_min=0, soft_max=1.0, step=3, precision=2)

    mult_fill_alpha : FloatProperty(name="Fill Alpha",
        description="Multiply Vertex fill color alpha (stroke color opacity)", 
        default=0.9, min=0, max=4.0, soft_max=2.0, precision=2, options={'HIDDEN'})

    # auto join
    proximity_tolerance : FloatProperty(name="Detection radius",
        description="Proximity tolerance (Relative to view)\
            \number of point detected in range printed in console", options={'HIDDEN'}, 
        default=0.01, min=0.00001, max=0.1, soft_min=0.0001, soft_max=0.1, step=3, precision=3)

    start_point_tolerance :  IntProperty(name="Head cutter tolerance", options={'HIDDEN'}, 
        description="Define number of points at the start of the last stroke that can be chosen\
            \n0 means only first point of the stroke is evaluated, new line will not be cutted",
        default=6, min=0, max=25, soft_max=8, step=1,)

    # polygonize
    poly_angle_tolerance : FloatProperty(name="Angle tolerance",
        description="Point with corner above this angle will be used as corners", 
        default=45, min=1, max=179, soft_min=5, soft_max=0.1, step=1, precision=1,
        options={'HIDDEN'},)

    # length tolerance
    length : bpy.props.FloatProperty(name="Length",
        description="Length tolerance", 
        default=0.010, min=0.0, max=1000, step=0.1, precision=4, options={'HIDDEN'})

    ## hatching settings
    ref_angle : bpy.props.IntProperty(name='Reference Angle', default=-45, 
        description='Reference angle to match from -90 to 90\
            \ne.g: / = -70, \ = 70, -- = 0')


### --- REGISTER ---

classes = (
GPR_refine_prop,
GPREFINE_OT_refine_ops,
GPREFINE_OT_straighten_stroke,
GPREFINE_OT_to_circle_shape,
GPREFINE_OT_polygonize,
)


def register():
    preferences.register()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gprsettings = PointerProperty(type = GPR_refine_prop)
    gp_selector.register()
    gp_harmonizer.register()
    ui.register()

    gp_keymaps.register()#keymaps

def unregister():
    del bpy.types.Scene.gprsettings
    gp_keymaps.unregister()#keymaps

    ui.unregister()
    gp_harmonizer.unregister()
    gp_selector.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    preferences.unregister()

if __name__ == "__main__":
    register()
