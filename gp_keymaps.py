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



addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    ## Set origin to cursor/geometry with ctrl+shift+alt+ extra mousebutton
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")# Grease Pencil # Grease Pencil Stroke Paint
    kmi = km.keymap_items.new("gp.delete_last_stroke", type = 'X', value = "PRESS", ctrl = False, shift = False, alt = True)
    # kmi.properties.type = 'ORIGIN_GEOMETRY'

    addon_keymaps.append(km)

    """ ## Jump to keyframe with alt + extra mousebutton
    km = addon.keymaps.new(name = "Window", space_type = "EMPTY")# valid in all editor
    #kmi = km.keymap_items.new("screen.keyframe_jump", type = "BUTTON6MOUSE", value = "PRESS")#mouse button above 5 aren't recognize on logitech mouse on windaube
    kmi = km.keymap_items.new("screen.keyframe_jump", type = key_prev, value = "PRESS", alt = True)
    kmi.properties.next = False
    #kmi = km.keymap_items.new("screen.keyframe_jump", type = "BUTTON7MOUSE", value = "PRESS")#mouse button above 5 aren't recognize on logitech mouse on windaube
    kmi = km.keymap_items.new("screen.keyframe_jump", type = key_next, value = "PRESS", alt = True)
    kmi.properties.next = True

    addon_keymaps.append(km)
    """

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        ## Can't (and supposedly shouldn't ) suppress original category name...
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

def register():
    if not bpy.app.background:
        register_keymaps() 

def unregister():
    if not bpy.app.background:
        unregister_keymaps()

if __name__ == "__main__":
    register()