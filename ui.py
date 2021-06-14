import bpy
from bpy.types import Panel
from . import addon_updater_ops
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
        addon_updater_ops.check_for_update_background()# updater
        addon_updater_ops.update_notice_box_ui(self, context)# updater

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

        layout.label(text='Points:')
        row = layout.row()
        row.operator('gp.select_by_angle', icon='PARTICLE_POINT')


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
        row.operator('gp.refine_strokes', text='-').action = 'SUB_LINE_HARDNESS'# Sub line_width
        row.operator('gp.refine_strokes', text='+').action = 'ADD_LINE_HARDNESS'# Add line_width

        row = layout.row()
        row.prop(context.scene.gprsettings, 'set_hardness')
        row.operator('gp.refine_strokes', text='Set hardness').action = 'SET_LINE_HARDNESS'

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

class GPREFINE_PT_auto_join(GPR_refine, Panel):
    bl_label = "Join Strokes"
    bl_parent_id = "GPREFINE_PT_stroke_refine_panel" # GPREFINE_PT_stroke_shape_refine subpanel of a subpanel
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        #-# (still )experimental Auto join
        # layout.use_property_split = True
        # layout.label(text='Auto-join:')
        layout.prop(context.scene.gprsettings, 'start_point_tolerance')
        layout.prop(context.scene.gprsettings, 'proximity_tolerance')
        layout.operator('gp.refine_strokes', text='Auto join', icon='CON_TRACKTO').action = 'GUESS_JOIN'

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


classes = (
GPREFINE_PT_stroke_refine_panel,#main panel
GPREFINE_PT_Selector,
GPREFINE_PT_stroke_shape_refine,
GPREFINE_PT_thickness_opacity,
GPREFINE_PT_resampling,
GPREFINE_PT_thin_tips,
GPREFINE_PT_auto_join,
GPREFINE_PT_analize_gp,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)