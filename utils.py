import bpy
import mathutils
from mathutils import Vector
import math
import numpy as np


def convertAttr(Attr):
    '''Convert given value to a Json serializable format'''
    if isinstance(Attr, (mathutils.Vector,mathutils.Color)):
        return Attr[:]
    elif isinstance(Attr, mathutils.Matrix):
        return [v[:] for v in Attr]
    elif isinstance(Attr,bpy.types.bpy_prop_array):
        return [Attr[i] for i in range(0,len(Attr))]
    else:
        return(Attr)

def location_to_region(worldcoords):
    from bpy_extras import view3d_utils
    return view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.space_data.region_3d, worldcoords)

def region_to_location(viewcoords, depthcoords):
    from bpy_extras import view3d_utils
    return view3d_utils.region_2d_to_location_3d(bpy.context.region, bpy.context.space_data.region_3d, viewcoords, depthcoords)


def transfer_value(Value, OldMin, OldMax, NewMin, NewMax):
    '''map a value from a range to another (transfer/translate value)'''
    return (((Value - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

def checkalign(a, b, tol=1e-6):
    '''Take two coord and check if they are close'''
    from math import isclose
    #base tolerance : 1e-6 (0.000001)
    if isclose(a[0], b[0], rel_tol=tol) and isclose(a[1], b[1], rel_tol=tol):
        return True
    return False

def checkalign3D(a, b, tol=1e-6):
    '''Take two coord and check if they are close'''
    from math import isclose
    #base tolerance : 1e-6 (0.000001)
    if isclose(a[0], b[0], rel_tol=tol) and isclose(a[1], b[1], rel_tol=tol) and isclose(a[2], b[2], rel_tol=tol):
        return True
    return False

def clamp(val, minimum, maximum):
    '''Return the value clamped to min-max'''
    return min(max(val, minimum), maximum)

""" 
def mean(*args):
    '''
    return mean of all passed value (multiple)
    If it's a list or tuple return mean of it.
    '''
    meanny = []
    for elem in args:
        if isinstance(elem, list) or isinstance(elem, tuple):
            meanny.append(mean(*elem))
        else:
            meanny.append(elem)
    return sum(meanny) / len(meanny)#sum(args) / len(args) #bad result !!! make a mean on sub portion and re-mean with the rest give false result
 """

def mean(*args):
    '''
    return mean of all passed value (multiple)
    If it's a list or tuple return mean of it (only on first list passed).
    '''
    if isinstance(args[0], list) or isinstance(args[0], tuple):
        return mean(*args[0])#send the first list UNPACKED (else infinite recursion as it always evaluate as list)
    return sum(args) / len(args)

def vector_len_from_coord(a, b):
    '''
    Get two points (that has coordinate 'co' attribute) or Vectors (2D or 3D)
    Return length as float
    '''
    from mathutils import Vector
    if type(a) is Vector:
        return (a - b).length
    else:   
        return (a.co - b.co).length

def align_obj_to_vec(obj, v):
    '''align rotation to given vector'''
    up_axis = Vector([0.0, 0.0, 1.0])
    angle = v.angle(up_axis, 0)
    axis = up_axis.cross(v)
    euler = Matrix.Rotation(angle, 4, axis).to_euler()
    obj.rotation_euler = euler

def debug_create_empty_from_vec(p,v):
    new_obj = bpy.data.objects.new('new_obj', None)
    new_obj.empty_display_type = 'ARROWS'
    new_obj.empty_display_size = 2#0.5
    new_obj.location = p
    align_obj_to_vec(new_obj, v)
    bpy.context.scene.collection.objects.link(new_obj)

def get_stroke_length(s):
    '''return 3D total length of the stroke'''
    all_len = 0.0
    for i in range(0, len(s.points)-1):
        #print(vector_len_from_coord(s.points[i],s.points[i+1]))
        all_len += vector_len_from_coord(s.points[i],s.points[i+1])   
    return (all_len)


def point_from_dist_in_segment_3d(a, b, ratio):
    '''return the tuple coords of a point on 3D segment ab according to given ratio (some distance divided by total segment lenght)'''
    ## ref:https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
    # ratio = dist / seglenght
    return ( ((1 - ratio) * a[0] + (ratio*b[0])), ((1 - ratio) * a[1] + (ratio*b[1])), ((1 - ratio) * a[2] + (ratio*b[2])) )

# -----------------
### Vector utils 2d
# -----------------

def get_stroke_2D_length(s):
    '''return 2D total length (relative to screen) of the stroke'''
    all_len = 0.0
    for i in range(0, len(s.points)-1):
        len_2D = vector_len_from_coord(location_to_region(s.points[i].co), location_to_region(s.points[i+1].co))
        all_len += len_2D
    return (all_len)

def vector_length_2d(A,B):
    ''''take two Vector and return length'''
    return sqrt((A[0] - B[0])**2 + (A[1] - B[1])**2)


def point_from_dist_in_segment_2d(a, b, dist, seglenght, as_int=False):
    '''return the tuple coords of a point on segment ab according to given distance and total segment lenght '''
    ## ref:https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
    ratio = dist / seglenght
    if as_int:#mode int (for opencv function)
        return ( int( ((1 - ratio) * a[0] + (ratio*b[0])) ), int( ((1 - ratio) * a[1] + (ratio*b[1])) ) )
    else:#float
        return ( ((1 - ratio) * a[0] + (ratio*b[0])), ((1 - ratio) * a[1] + (ratio*b[1])) )

def cross_vector_coord_2d(foo, bar, size):
    '''Return the coord in space of a cross vector between the two point with specified size'''
    ###middle location between 2 vector is calculated by adding the two vector and divide by two
    ##mid = (foo + bar) / 2
    between = foo - bar
    #create a generic Up vector (on Y or Z)
    up = Vector([0,1.0])
    new = Vector.cross(up, between)#the cross product return a 90 degree Vector
    if new == Vector([0.0000, 0.0000]):
        #new == 0 if up vector and between are aligned ! (so change up vector)
        up = Vector([0,-1.0,0])
        new = Vector.cross(up, between)#the cross product return a 90 degree Vector

    perpendicular = foo + new
    coeff = vector_length_coeff(size, foo, perpendicular)
    #position the point in space by adding the new vector multiplied by coeff value to get wanted lenght
    return (foo + (new * coeff))


def midpoint_2d(p1, p2):
    return (Vector([(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]))


def get_angle_from_points(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

def get_angle(v0, v1):
    '''get two vector, return signed angle in degree'''
    return np.degrees( np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1)) )


def get_ninety_angle_from(a, b):
    '''Get angle from horizon bewteen 0 (->) and 90
    up      : -90
    horizon : 0
    down    : 90
    '''
    H = Vector((1,0))
    #res = degrees( H.angle(b-a) )
    V = b-a
    if V == Vector((0,0)):
        return
    angle = H.angle_signed(b-a)
    res = math.degrees(angle)
    
    if res > 90:
        res = res - 180
    if res < -90:
        res = res + 180
    return res