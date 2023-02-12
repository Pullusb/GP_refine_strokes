import bpy

def get_addon_prefs():
    '''
    function to read current addon preferences properties
    access with : get_addon_prefs().super_special_option
    '''
    import os
    addon_name = os.path.splitext(__name__)[0]
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return (addon_prefs)


def update_ui(context, scene):
    # Cannot import ui outside (import from partially initialzed module)
    from . import ui 
    if get_addon_prefs().experimental:
        # print('Experimental features On')
        try:
            ui.register_experimental()
        except:
            print('Could not register experimental features')
        
    else:
        # print('Experimental features Off')
        try:
            ui.unregister_experimental()
        except Exception as e:
            print('Could not unregister experimental features')
            print(e)

class GPR_addonprefs(bpy.types.AddonPreferences):
    bl_idname = __name__.split('.')[0]
    
    experimental : bpy.props.BoolProperty(name='Enable Experimental Features',
        description='Enable experimental features. Unstable or beta',
        default=False, update=update_ui)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'experimental')



classes=(
GPR_addonprefs,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


