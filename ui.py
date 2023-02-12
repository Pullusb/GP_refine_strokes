import bpy
from bpy.types import Panel
from .preferences import get_addon_prefs
### PANELS ----

#generic class attribute and poll for following panels
class GPR_refine:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Gpencil"
    # bl_options = {'DEFAULT_CLOSED'}

    # @classmethod
    # def poll(cls, context):
    #     return (context.object is not None and context.object.type == 'GPENCIL')

class GPREFINE_PT_stroke_refine_panel(GPR_refine, Panel):
    bl_label = "Strokes Refine"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True # send properties to the right side

        col_filter = layout.column()
        col_filter.prop(context.scene.gprsettings, 'layer_tgt')
        col_filter.prop(context.scene.gprsettings, 'frame_tgt')
        col_filter.prop(context.scene.gprsettings, 'stroke_tgt')
        
        col_filter.active = not (context.scene.gprsettings.use_select or (context.scene.gprsettings.use_context and context.mode == 'PAINT_GPENCIL'))

        col_pref = layout.column()
        col_pref.prop(context.scene.gprsettings, 'use_context')
        col_pref.prop(context.scene.gprsettings, 'use_select')
        
        #-# Updater


class GPREFINE_PT_Selector(GPR_refine, Panel):
    bl_label = "Selections"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        layout.label(text='Strokes:')

        row = layout.row(align=True)
        row.operator('gp.backward_selector', text='Select Backward', icon='TRACKING_BACKWARDS').deselect = False
        row.operator('gp.backward_selector', text='Deselect Backward').deselect = True

        row = layout.row(align=True)
        row.prop(context.scene.gprsettings, 'length')
        row.operator('gp.select_by_length', text='Select', icon='DRIVER_DISTANCE')

        col = layout.column(align=True)        
        row = col.row(align=True)

        row.prop(context.scene.gprsettings, 'ref_angle', text='Angle', icon='DRIVER_ROTATIONAL_DIFFERENCE')
        row.operator('gp.hatching_selector', icon='OUTLINER_DATA_LIGHTPROBE').ref_angle = context.scene.gprsettings.ref_angle
        col.operator('gp.set_angle_from_stroke')
        
        layout.operator('gp.attribute_selector')
        layout.operator('gp.coplanar_selector')

        layout.label(text='Points:')
        row = layout.row()
        row.operator('gp.select_by_angle', icon='PARTICLE_POINT')

## Thickness and opacity panel

class GPREFINE_PT_thickness_opacity(GPR_refine, Panel):
    bl_label = "Thickness And Opacity"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

class GPREFINE_PT_line_width(GPR_refine, Panel):
    bl_label = "Line Width"
    bl_parent_id = "GPREFINE_PT_thickness_opacity"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene.gprsettings, 'add_line_width', text='Add Width') #, text='Add Line Width'
        row.operator('gp.refine_strokes', text='-').action = 'SUB_LINE_WIDTH'# Sub line_width
        row.operator('gp.refine_strokes', text='+').action = 'ADD_LINE_WIDTH'# Add line_width
        row = col.row()
        row.prop(context.scene.gprsettings, 'set_line_width', text='Set Width') #, text='Set Line Width'
        row.operator('gp.refine_strokes', text='Set line width').action = 'SET_LINE_WIDTH'
        row = col.row()
        row.prop(context.scene.gprsettings, 'mult_line_width', text='Multiply Width') #, text='Multiply Width'
        row.operator('gp.refine_strokes', text='*').action = 'MULT_LINE_WIDTH'

        col = layout.column(align=True)
        col.operator('gp.lines_harmonizer', text='Equalize Line Thickness').attribute = 'line_width'

class GPREFINE_PT_line_hardness(GPR_refine, Panel):
    bl_label = "Line Hardness"
    bl_parent_id = "GPREFINE_PT_thickness_opacity"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene.gprsettings, 'add_hardness', text='Add Hardness')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_LINE_HARDNESS'
        row.operator('gp.refine_strokes', text='+').action = 'ADD_LINE_HARDNESS'

        row = col.row()
        row.prop(context.scene.gprsettings, 'set_hardness', text='Set Hardness')
        row.operator('gp.refine_strokes', text='Set hardness').action = 'SET_LINE_HARDNESS'

        row = col.row()
        row.prop(context.scene.gprsettings, 'mult_line_hardness', text='Multiply Hardness')
        row.operator('gp.refine_strokes', text='*').action = 'MULT_LINE_HARDNESS'

class GPREFINE_PT_point_pressure(GPR_refine, Panel):
    bl_label = "Point Pressure"
    bl_parent_id = "GPREFINE_PT_thickness_opacity"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene.gprsettings, 'add_pressure', text='Add Pressure')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_PRESSURE'# Sub pressure
        row.operator('gp.refine_strokes', text='+').action = 'ADD_PRESSURE'# Add pressure
        
        row = col.row()
        row.prop(context.scene.gprsettings, 'set_pressure', text='Set Pressure')
        row.operator('gp.refine_strokes', text='Set pressure').action = 'SET_PRESSURE'#, icon='GREASEPENCIL'

        row = col.row()
        row.prop(context.scene.gprsettings, 'mult_pressure', text='Multiply Pressure')
        row.operator('gp.refine_strokes', text='*').action = 'MULT_PRESSURE'

        col = layout.column(align=True)
        col.operator('gp.lines_harmonizer', text='Equalize Point Pressure').attribute = 'point_pressure'


class GPREFINE_PT_point_strength(GPR_refine, Panel):
    bl_label = "Point Strength"
    bl_parent_id = "GPREFINE_PT_thickness_opacity"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene.gprsettings, 'add_strength', text='Add Strength')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_STRENGTH'# Sub strength
        row.operator('gp.refine_strokes', text='+').action = 'ADD_STRENGTH'# Add strength
        
        row = col.row()
        row.prop(context.scene.gprsettings, 'set_strength', text='Set Strength')
        row.operator('gp.refine_strokes', text='Set strength').action = 'SET_STRENGTH'#, icon='GREASEPENCIL'

        row = col.row()
        row.prop(context.scene.gprsettings, 'mult_strength', text='Multiply Strength')
        row.operator('gp.refine_strokes', text='*').action = 'MULT_STRENGTH'

class GPREFINE_PT_point_alpha(GPR_refine, Panel):
    bl_label = "Point Alpha"
    bl_parent_id = "GPREFINE_PT_thickness_opacity"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene.gprsettings, 'add_alpha', text='Add Alpha')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_ALPHA'
        row.operator('gp.refine_strokes', text='+').action = 'ADD_ALPHA'
        
        row = col.row()
        row.prop(context.scene.gprsettings, 'set_alpha', text='Set Alpha')
        row.operator('gp.refine_strokes', text='Set alpha').action = 'SET_ALPHA'

        row = col.row()
        row.prop(context.scene.gprsettings, 'mult_alpha', text='Multiply Alpha')
        row.operator('gp.refine_strokes', text='*').action = 'MULT_ALPHA'

class GPREFINE_PT_stroke_fill_alpha(GPR_refine, Panel):
    bl_label = "Stroke Fill Alpha"
    bl_parent_id = "GPREFINE_PT_thickness_opacity"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene.gprsettings, 'add_fill_alpha', text='Add Fill Alpha')
        row.operator('gp.refine_strokes', text='-').action = 'SUB_FILL_ALPHA'# Sub vertex color alpha
        row.operator('gp.refine_strokes', text='+').action = 'ADD_FILL_ALPHA'# Add vertex color alpha
        
        row = col.row()
        row.prop(context.scene.gprsettings, 'set_fill_alpha', text='Set Fill Alpha')
        row.operator('gp.refine_strokes', text='Set alpha').action = 'SET_FILL_ALPHA'

        row = col.row()
        row.prop(context.scene.gprsettings, 'mult_fill_alpha', text='Multiply Fill Alpha')
        row.operator('gp.refine_strokes', text='*').action = 'MULT_FILL_ALPHA'

# class GPREFINE_PT_harmonizer(GPR_refine, Panel):
#     bl_label = "Harmonizer"#"Strokes filters"
#     bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
#     # bl_options = {'DEFAULT_CLOSED'}

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         col = layout.column(align=False)

#         col.operator('gp.lines_harmonizer', text='Line Thickness').attribute = 'line_width'
#         col.operator('gp.lines_harmonizer', text='Point Pressure').attribute = 'point_pressure'

class GPREFINE_PT_stroke_shape_refine(GPR_refine, Panel):
    bl_label = "Stroke Reshape"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        
        ## Deleter
        row = layout.row()
        row.operator('gp.backward_stroke_delete', icon='TRACKING_CLEAR_BACKWARDS') # GPBRUSH_ERASE_STROKE

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
        # row.operator('gp.select_by_angle', icon='PARTICLE_POINT')
        row.operator('gp.polygonize_stroke', icon='LINCURVE')
        
        # row.operator('gp.refine_strokes', text='Polygonize', icon='IPO_CONSTANT').action = 'POLYGONIZE' # generic polygonize


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

class GPREFINE_PT_analize_gp(GPR_refine, Panel):
    bl_label = "Infos"#"Strokes filters"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        col.operator('gp.refine_strokes', text='Print Stroke Infos', icon = 'GP_SELECT_POINTS').action = 'INSPECT_STROKES'
        col.operator('gp.refine_strokes', text='Print Points Infos', icon = 'SNAP_MIDPOINT').action = 'INSPECT_POINTS'
        col.operator('gp.refine_strokes', text='List Pressure', icon = 'STYLUS_PRESSURE').action = 'POINTS_PRESSURE_INFOS'

class GPREFINE_PT_thin_tips(GPR_refine, Panel):
    bl_label = "Thin Stroke Tips"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel"
    bl_options = {'DEFAULT_CLOSED'}

    # def draw_header(self, context):
    #     layout = self.layout
    #     layout.label(text='', icon='ERROR')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        col.label(text='(experimental)', icon='ERROR')
        # row = layout.row()
        col.prop(context.scene.gprsettings, 'percentage_use_sync_tip_len')
        if context.scene.gprsettings.percentage_use_sync_tip_len:
            col.prop(context.scene.gprsettings, 'percentage_tip_len')
        else:
            col.prop(context.scene.gprsettings, 'percentage_start_tip_len')
            col.prop(context.scene.gprsettings, 'percentage_end_tip_len')
        col.prop(context.scene.gprsettings, 'force_max_pressure_line_body')
        col.operator('gp.refine_strokes', text='Full And Thin Strokes').action = 'THIN_RELATIVE'
        # layout.label(text="Those settings only affect additive or eraser mode")


class GPREFINE_PT_auto_join(GPR_refine, Panel):
    bl_label = "Join Strokes"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel" # GPREFINE_PT_stroke_shape_refine subpanel of a subpanel
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        #-# (still )experimental Auto join
        col.label(text='(experimental)', icon='ERROR')
        col.prop(context.scene.gprsettings, 'start_point_tolerance')
        col.prop(context.scene.gprsettings, 'proximity_tolerance')
        col.operator('gp.refine_strokes', text='Auto join', icon='CON_TRACKTO').action = 'GUESS_JOIN'

classes = (
GPREFINE_PT_stroke_refine_panel,
GPREFINE_PT_Selector,
GPREFINE_PT_stroke_shape_refine,

GPREFINE_PT_thickness_opacity,
GPREFINE_PT_line_width,
GPREFINE_PT_point_pressure,
GPREFINE_PT_point_strength,
GPREFINE_PT_point_alpha,
GPREFINE_PT_stroke_fill_alpha,
GPREFINE_PT_line_hardness,

GPREFINE_PT_resampling,
GPREFINE_PT_analize_gp,
)

experimental = (
GPREFINE_PT_thin_tips,
GPREFINE_PT_auto_join,
)

def register_experimental():
    for cls in experimental:
        bpy.utils.register_class(cls)

def unregister_experimental():
    for cls in reversed(experimental):
        bpy.utils.unregister_class(cls)

# ---

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    if get_addon_prefs().experimental:
        register_experimental()

def unregister():
    if get_addon_prefs().experimental:
        unregister_experimental()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)