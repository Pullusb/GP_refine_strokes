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

import bpy
# from .utils import *
# from .gpfunc import *
from . import gpfunc
import numpy as np

class GPREFINE_OT_lines_harmonizer(Operator):
    bl_idname = "gp.lines_harmonizer"
    bl_label = "Line Harmonizer"
    bl_description = "Level an attribute. Define min/max and how much it affects the lines"
    bl_options = {"REGISTER", "UNDO"}

    attribute : StringProperty(name="Attribute",
        description="Line attribute to harmonize", default="point_pressure", maxlen=0)
    
    influence : bpy.props.FloatProperty(name="Influence", 
        description="Influence Percentage to harmonize at reference level", 
        default=100, min=1, max=100, step=2, precision=1, subtype='PERCENTAGE', unit='NONE')
    
    ref_fac : bpy.props.FloatProperty(name="Reference Level",
        description="Reference level to harmonize attribute\
            \n0.5 is median value, 1 = max value, 0 is min value", 
        default=0.5, soft_min=0.0, soft_max=1.0, min=-2.0, max=2.0, step=2, precision=2)
    
    # only_stroke : bpy.props.BoolProperty(name="Stroke Mateiral only", 
    #     description="Filter to affect only stroke materials", default=False)
    
    individually : bpy.props.BoolProperty(name="Affect Strokes Individually", 
        description="Set the reference by strokes instead of global", default=False)

    ## Line Width
    ## Point Pressure
    ## Overall Thickness (point + line)
    ## Alpha

    def invoke(self, context, event):
        self.shift = event.shift
        # pref = context.scene.gprsettings
        self.L, self.F, self.S = gpfunc.get_context_scope(context)
        
        if self.attribute == 'line_width':
            attr_list = gpfunc.get_line_attr('line_width', self.L, self.F, self.S)
        elif self.attribute == 'point_pressure':
            attr_list = gpfunc.get_point_attr('pressure', self.L, self.F, self.S)
        
        if not attr_list:
            self.report({'ERROR'}, 'Nothing found, check Stroke filter')
            return {"CANCELLED"}
        
        self.count = len(attr_list)
        self.min = min(attr_list)
        self.max = max(attr_list)
        
        # if self.method == 'MEAN': # Average
        #     comp_func = np.mean
        # elif self.method == 'MEDIAN': # Middle value
        #     comp_func = np.median

        # self.target_val = self.min + (self.max - self.min) * self.ref_fac
        self.mean = np.mean(attr_list)
        self.median = np.median(attr_list)

        print('self.min: ', self.min)
        print('self.max: ', self.max)
        print('self.mean: ', self.mean)
        print('self.median: ', self.median)

        self.target_val = 0 # will be calculated at beginning of 
        print('self.target_val: ', self.target_val)
        # if self.target == "point_pressure":
        #     gp_add_line_attr('line_width', amount=pref.add_line_width, t_layer=L, t_frame=F, t_stroke=S)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "influence")
        layout.prop(self, "ref_fac")
        layout.prop(self, "individually")
        # layout.prop(self, "only_stroke")
        
        layout.label(text='infos:')
        row = layout.row()
        if isinstance(self.max, int):
            row.label(text=f'min: {self.min}')
            row.label(text=f'max: {self.max}')
            row = layout.row()
            row.label(text=f'mean: {self.mean:.3f}')
            row.label(text=f'median: {self.median:.3f}')
        else:
            row.label(text=f'min: {self.min:.3f}')
            row.label(text=f'max: {self.max:.3f}')
            row = layout.row()
            row.label(text=f'mean: {self.mean:.3f}')
            row.label(text=f'median: {self.median:.3f}')
        
        if not self.individually:
            ## Makes no sense in global mode
            row = layout.row()
            row.label(text=f'Target: {self.target_val:.3f}')
        

    def execute(self, context):
        fac = self.influence / 100
        err = None
        self.target_val = self.min + (self.max - self.min) * self.ref_fac

        if self.attribute == 'point_pressure':
            attr_type = 'pressure'

            for s in gpfunc.strokelist(self.L, self.F, self.S):
                ## Scale with a multiplier so top level point in the stroke reach reference value
                pts_val = [0.0] * len(s.points)
                s.points.foreach_get(attr_type, pts_val)
                max_v = max(pts_val)
                if max_v == 0:
                    # Skip. Can't divide by 0
                    continue
    
                stroke_fac = self.target_val / max_v
                # print(max_v)
                # print('stroke_fac: ', stroke_fac)

                ## modulate stroke factor by influence amount
                modulated_fac = 1 - ((1 - stroke_fac) * fac)
                # print('modulated_fac: ', modulated_fac)
                
                s.points.foreach_set(attr_type, np.array(pts_val) * modulated_fac)
                s.points.update()

                # ## Set all to value (interesting ? can be done with set)
                # for p in s.points:
                #     val = getattr(p, attr_type)
                #     setattr(p, attr_type, val + (self.target_val - val) * fac)


        if self.attribute == 'line_width':
            for s in gpfunc.strokelist(self.L, self.F, self.S):
                s.line_width = s.line_width + int((self.target_val - s.line_width) * fac)


        if err is not None:
            self.report({'ERROR'}, err)
        return {"FINISHED"}


classes =(
    GPREFINE_OT_lines_harmonizer,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)