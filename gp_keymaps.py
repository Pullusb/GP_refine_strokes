import bpy
from bpy.types import Operator
from .gpfunc import delete_last_stroke

class GPREFINE_OT_delete_last_stroke(bpy.types.Operator):
    bl_idname = "gp.delete_last_stroke"
    bl_label = "Delete last GP strokes"
    bl_description = "Delete the last grease pencil stroke of the active layer and frame"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'GPENCIL' and context.mode == 'PAINT_GPENCIL'

    def execute(self, context):
        mess = delete_last_stroke()
        if mess:
            self.report({mess[0]}, mess[1])
            return {"CANCELLED"}
        return {"FINISHED"}



class GPREFINE_OT_stroke_eraser(bpy.types.Operator):
    bl_idname = "wm.stroke_eraser"
    bl_label = "Secondary stroke eraser"
    bl_description = "Temporary use a secondary eraser"
    bl_options = {'REGISTER', 'INTERNAL'}#, no 'UNDO', avoid register undo step

    _is_running = False# block subsequent 'PRESS' events
    # bpy.types.Scene.tmp_cutter_org_mode = bpy.props.StringProperty(
    bpy.types.WindowManager.tmp_tool_org_mode = bpy.props.StringProperty(
        name="temp tool previous mode", description="Use to store mode used before cutter", default="")
    bpy.types.WindowManager.tmp_eraser_org_mode = bpy.props.StringProperty(
        name="temp tool previous mode", description="Use to store Eraser mode used before cutter", default="")
    # bpy.types.WindowManager.tmp_eraser_radius_org_mode = bpy.props.IntProperty(
    #     name="", description="store initial radius"

    def execute(self, context):
        # print('exe so cute')
        bpy.ops.wm.tool_set_by_id(name='builtin_brush.Erase')
        context.window_manager.tmp_eraser_org_mode = context.scene.tool_settings.gpencil_paint.brush.name
        eraser = bpy.data.brushes.get('Eraser Stroke')
        if not eraser:
            self.report({'ERROR'}, "'Eraser Stroke' not found")
            return {'CANCELLED'}
        context.scene.tool_settings.gpencil_paint.brush = eraser
        
        # - size
        # context.window_manager.tmp_eraser_radius_org_mode = eraser.size
        # eraser.size = 8
        
        return {'FINISHED'}

    def invoke(self, context, event):
        print('event.value: ', event.value)
        if event.value == 'RELEASE':
            __class__._is_running = False
            
            wm = context.window_manager
            # if self.original_mode:
            #     bpy.ops.wm.tool_set_by_id(name = self.original_mode)
            if hasattr(wm, 'tmp_eraser_org_mode'):
                context.scene.tool_settings.gpencil_paint.brush = bpy.data.brushes[context.window_manager.tmp_eraser_org_mode]
                ## set default brush, else it's ctrl+Click call last USED
                context.scene.tool_settings.gpencil_paint.brush.gpencil_settings.use_default_eraser = True

            # print('Release ->', wm.tmp_tool_org_mode)
            if hasattr(wm, 'tmp_tool_org_mode'):
                bpy.ops.wm.tool_set_by_id(name = 'builtin_brush.Draw')
                # bpy.ops.wm.tool_set_by_id(name = wm.tmp_tool_org_mode)

            # return 'CANCELLED' unless the code is important,
            # this prevents updating the view layer unecessarily
            return {'CANCELLED'}


        elif event.value == 'PRESS':
            if not self._is_running:
                # self.original_mode = bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode, create=False).idname
                context.window_manager.tmp_tool_org_mode = bpy.context.workspace.tools.from_space_view3d_mode(context.mode, create=False).idname


                __class__._is_running = True
                return self.execute(context)
            print('GPREFINE_OT_stroke_eraser (id_name: wm.stroke_eraser) is already running. could not launch secondary Eraser')

        return {'CANCELLED'}

### tried to just change the default eraser but doesn't work.
""" class GPREFINE_OT_stroke_eraser(bpy.types.Operator):
    bl_idname = "wm.stroke_eraser"
    bl_label = "Secondary stroke eraser"
    bl_description = "Temporary use a secondary eraser"
    bl_options = {'REGISTER', 'INTERNAL'}#, no 'UNDO', avoid register undo step

    _is_running = False# block subsequent 'PRESS' events
    # bpy.types.Scene.tmp_cutter_org_mode = bpy.props.StringProperty(

    bpy.types.WindowManager.tmp_default_eraser = bpy.props.StringProperty(
        name="temp tool previous mode", description="Use to store Eraser mode used before cutter", default="")
    # bpy.types.WindowManager.tmp_eraser_radius_org_mode = bpy.props.IntProperty(
    #     name="", description="store initial radius"

    def execute(self, context):
        # print('exe so cute')

        # eraser = bpy.data.brushes.get('Eraser Stroke')
        # if not eraser:
        #     self.report({'ERROR'}, "'Eraser Stroke' not found")
        #     return {'CANCELLED'}
        

        # - size
        # context.window_manager.tmp_eraser_radius_org_mode = eraser.size
        # eraser.size = 8
        
        return {'CANCELLED'}

    def invoke(self, context, event):
        print('event.value: ', event.value)
        if event.value == 'RELEASE':
            print('release')
            __class__._is_running = False

            org_eraser = bpy.data.brushes.get(context.window_manager.tmp_default_eraser)
            ## set default brush, else it's ctrl+Click call last USED
            org_eraser.gpencil_settings.use_default_eraser = True

            # return 'CANCELLED' unless the code is important,
            # this prevents updating the view layer unecessarily
            return {'CANCELLED'}


        elif event.value == 'PRESS':
            if not self._is_running:
                # self.original_mode = bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode, create=False).idname
                eraser_stroke = bpy.data.brushes.get('Eraser Stroke')
                if not eraser_stroke:
                    self.report({'ERROR'}, '"Eraser Stroke" not found')
                    return {'CANCELLED'}

                for b in bpy.data.brushes:
                    if hasattr(b, 'gpencil_settings'):
                        if b.gpencil_settings:
                            if b.name.startswith('Eraser'):
                                if b.gpencil_settings.use_default_eraser:
                                    context.window_manager.tmp_default_eraser = b.name
                                # print('>', b.name, b.gpencil_settings.use_default_eraser)

                eraser_stroke.gpencil_settings.use_default_eraser = True

                __class__._is_running = True
                return self.execute(context)
            print('GPREFINE_OT_stroke_eraser (id_name: wm.stroke_eraser) is already running. could not launch secondary Eraser')

        return {'CANCELLED'} """

addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    ## Set origin to cursor/geometry with ctrl+shift+alt+ extra mousebutton
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")# Grease Pencil # Grease Pencil Stroke Paint
    kmi = km.keymap_items.new("gp.delete_last_stroke", type = 'X', value = "PRESS", ctrl = False, shift = False, alt = True)
    # kmi.properties.type = 'ORIGIN_GEOMETRY'

    addon_keymaps.append((km, kmi))

    # - # Shortcut to custom modal stroke eraser
    # km = addon.keymaps.new(name = "Grease Pencil Stroke Paint (Draw brush)", space_type = "EMPTY")# Grease Pencil # Grease Pencil Stroke Paint
    # kmi = km.keymap_items.new("wm.stroke_eraser", type = 'S', value = "PRESS")
    # kmi.repeat = True
    # addon_keymaps.append((km, kmi))

    # # - # not in the right context in eraser mode for the release, map the same
    # km = addon.keymaps.new(name = "Grease Pencil Stroke Paint (Erase)", space_type = "EMPTY")# Grease Pencil # Grease Pencil Stroke Paint
    # kmi = km.keymap_items.new("wm.stroke_eraser", type = 'S', value = "RELEASE")
    # kmi.repeat = False
    # addon_keymaps.append((km, kmi))
    
    # ---
    # - # shortcut to native eraser
    # km = addon.keymaps.new(name = "Grease Pencil Stroke Paint (Draw brush)", space_type = "EMPTY")
    # # kmi = km.keymap_items.new("gpencil.draw", type = 'S', value = "PRESS")
    # kmi = km.keymap_items.new("gpencil.draw", type = 'LEFTMOUSE', value = "PRESS", key_modifier='S')
    # #kmi.repeat = False
    # kmi.repeat = True
    # # kmi.draw = "ERASER"
    # addon_keymaps.append((km, kmi))


    """ ## Jump to keyframe with alt + extra mousebutton (keymapped in Mykeymouse)
    km = addon.keymaps.new(name = "Window", space_type = "EMPTY")# valid in all editor
    #kmi = km.keymap_items.new("screen.keyframe_jump", type = "BUTTON6MOUSE", value = "PRESS")# mouse button above 5 aren't recognize on logitech mouse on windaube
    kmi = km.keymap_items.new("screen.keyframe_jump", type = key_prev, value = "PRESS", alt = True)
    kmi.properties.next = False
    #kmi = km.keymap_items.new("screen.keyframe_jump", type = "BUTTON7MOUSE", value = "PRESS")# mouse button above 5 aren't recognize on logitech mouse on windaube
    kmi = km.keymap_items.new("screen.keyframe_jump", type = key_next, value = "PRESS", alt = True)
    kmi.properties.next = True

    addon_keymaps.append(km)
    """

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


classes = (
GPREFINE_OT_delete_last_stroke,
# GPREFINE_OT_stroke_eraser,
)

def register():
    if not bpy.app.background:
        for cls in classes:
            bpy.utils.register_class(cls)

        register_keymaps() 

def unregister():
    if not bpy.app.background:
        unregister_keymaps()
    
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()