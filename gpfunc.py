from .utils import *
import bpy
import mathutils
from mathutils import Vector
from math import acos, degrees
import numpy as np
import json

### -- GET STROKES FILTERS --

def get_layers(target='SELECT'):
    '''
    Return an iterable list of layer according to keywords target string
    SELECT (default), ACTIVE, ALL, SIDE_SELECT, UNRESTRICTED
    Return empty list if nothing found
    '''
    if not bpy.context.object.type == 'GPENCIL': return []
    if not bpy.context.object.data.layers.active: return []
    
    if not target or target == 'SELECT':# iterable with all selected layer (dopesheet)
        # return [l for l in bpy.context.object.data.layers if l.select and not l.hide and not l.lock]
        ## seems it can sometimes bug when there is an active that is not selected (should be selected) 
        return [l for l in bpy.context.object.data.layers if l ==  bpy.context.object.data.layers.active and not l.hide and not l.lock or l.select and not l.hide and not l.lock]

    elif target == 'ACTIVE':# iterable with only active layer
        return [bpy.context.object.data.layers.active]

    elif target == 'ALL': # all visible and unlocked layers iterable
        return [l for l in bpy.context.object.data.layers if not l.hide and not l.lock]

    elif target == 'SIDE_SELECT':# iterable with all selected layer except active
        if bpy.context.object.data.layers.active and len([l for l in bpy.context.object.data.layers if l.select and not l.hide and not l.lock]) > 1:
            return [l for l in bpy.context.object.data.layers if l.select and not l.hide and not l.lock and l != bpy.context.object.data.layers.active]
    
    elif target == 'UNRESTRICTED': # all layers iterable (everything)
        return bpy.context.object.data.layers

    return []

def get_frames(layer, target='ACTIVE'):
    '''
    Get a layer and return active frame or all frame as iterable
    ACTIVE default, ALL, SELECT, 
    Return empty list if nothing found
    '''
    if not layer.active_frame:return []

    if not target or target == 'ACTIVE':#iterable with active frame
        return  [layer.active_frame]
    
    elif target == 'ALL':#iterable of all frames in layer
        return layer.frames
    
    elif target == 'SELECT':#iterable of all selected frames in layer
        return [f for f in layer.frames if f.select]

    return []

def get_strokes(frame, target='SELECT'):
    '''
    Return an iterable list of layer according to keywords target string
    SELECT (default), ALL, LAST
    Return empty list if nothing found
    '''
    if not len(frame.strokes):return []
    
    if not target or target == 'SELECT':
        return  [s for s in frame.strokes if s.select]
    
    elif target == 'ALL':
        return frame.strokes
    
    elif target == 'LAST':
        return [frame.strokes[-1]]
    
    return []  

def strokelist(t_layer='ALL', t_frame='ACTIVE', t_stroke='SELECT'):
    '''
    Quickly return a strokelist according to given filters
    By default - All accessible on viewport : visible and unlocked
    '''
    ## TODO: when stroke is LAST and layer is ALL it can be the last of all layers, priority must be set to active layer.

    return [[[s for s in get_strokes(f, target=t_stroke)] for f in get_frames(l, target=t_frame)] for l in get_layers(target=t_layer)][0][0]

def get_last_stroke():
    return bpy.context.object.data.layers.active.active_frame.strokes[-1]

def selected_strokes():
    strokes = []
    for l in bpy.context.object.data.layers:
        if not l.hide and not l.lock:
            for s in l.active_frame.strokes:
                if s.select:
                    strokes.append(s)
    return(strokes)

### -- FUNCTIONS --

## -- overall pressure and strength


def gp_add_line_width(amount, t_layer='SELECT', t_frame='ACTIVE', t_stroke='SELECT'):
    for s in strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke):
        s.line_width += amount

def gp_set_line_width(amount, t_layer='SELECT', t_frame='ACTIVE', t_stroke='SELECT'):
    for s in strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke):
        s.line_width = amount

def gp_add_pressure(amount, t_layer='SELECT', t_frame='ACTIVE', t_stroke='SELECT'):
    for s in strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke):
        for p in s.points:
            p.pressure += amount

def gp_set_pressure(amount, t_layer='SELECT', t_frame='ACTIVE', t_stroke='SELECT'):
    for s in strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke):
        #TODO use a foreach_set on points for speed
        for p in s.points:
            p.pressure = amount

def gp_add_strength(amount, t_layer='SELECT', t_frame='ACTIVE', t_stroke='SELECT'):
    for s in strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke):
        for p in s.points:
            p.strength += amount

def gp_set_strength(amount, t_layer='SELECT', t_frame='ACTIVE', t_stroke='SELECT'):
    for s in strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke):
        #TODO use a foreach_set on points for speed
        for p in s.points:
            p.strength = amount

## -- thinner tips

def abs_thinner_tip(s, tip_len=5, middle=0):
    '''
    Get a stroke and a number of point to make the interpolation
    give weird results
    '''
    e = len(s.points)
    for j, pt in enumerate(s.points):
        if j <= tip_len:
            normval = (j - 0) / (tip_len - 0)
            # print("j", j)#Dbg
            # print("normval", normval)#Dbg
            pt.pressure = normval
        if e <= tip_len:
            normval = (e - 0) / (tip_len - 0)
            # print("e", e)#Dbg
            # print("normval", normval)#Dbg
            pt.pressure = normval
        if middle and j > tip_len and e > tip_len:
            pt.pressure = middle
        e -= 1

def get_tip_from_percentage(s, tip_len=20, variance=0):
    '''
    Get a stroke and percentage
    return points number and number of points given a percentage from tip to middle of stroke (100%)
    '''
    p_num = len(s.points)#total number of points
    # limit = p_num//2#middle of the points
    # if limit < 2:
    if p_num < 4:
        print ('Not enough points to thin tip correctly')
        return
    if variance:
        import random
        tip_len = min(max(tip_len + random.randint(-variance, variance), 5),100)

    # thin_range = int( limit * tip_len/100)+1 #unnacurate percentage (of half the line) in point number
    thin_range = int(p_num * tip_len/100)+1 #unnacurate percentage in point number
    print(f'zone: {thin_range}/{p_num}')#Dbg
    return thin_range

def reshape_rel_thinner_tip_percentage(s, tip_len=10, variance=0):
    '''
    Make points's pressure of strokes thinner by a point number percentage value (on total)
    value is a percentage (of half a line min 10 percent, max 100)
    variance randomize the tip_len by given value (positive or negative)
    '''
    thin_range = get_tip_from_percentage(s, tip_len=tip_len, variance=variance)
    # Get pressure of point to fade from as reference. 
    #+1 To get one further point as a reference but dont affect it (no change if relaunch except if variance).
    start_max = s.points[thin_range+1].pressure 
    end_max = s.points[-thin_range-1].pressure  #-1 Same stuff
    for i in range(thin_range):
        # print(i, 'start ->', transfer_value(i, 0, thin_range, 0.1, start_max) )
        # print(i, 'end ->', transfer_value(i, 0, thin_range, 0.1, end_max) )
        s.points[i].pressure = transfer_value(i, 0, thin_range, 0.1, start_max)
        s.points[-(i+1)].pressure = transfer_value(i, 0, thin_range, 0.1, end_max)

    #average value ?
    """ # get pressure of average max...
    import statistics
    pressure_list = [p.pressure for p in s.points if p.pressure > 0.1]
    if not pressure_list:
        pressure_list = [p.pressure for p in s.points if p.pressure]
    average = statistics.mean(pressure_list)"""
    return 0

def reshape_abs_thinner_tip_percentage(s, tip_len=10, variance=0):
    '''
    Make points's pressure of strokes thinner by a point number percentage value (on total)
    All stroke will get max value
    '''
    thin_range = get_tip_from_percentage(s, tip_len=tip_len, variance=variance)
    max_pressure = max([p.pressure for p in s.points])
    for i in range(thin_range):#TODO : Transfer based on a curve to avoid straight fade.
        s.points[i].pressure = transfer_value(i, 0, thin_range, 0.1, max_pressure)
        s.points[-(i+1)].pressure = transfer_value(i, 0, thin_range, 0.1, max_pressure)

def info_pressure(t_layer='ACTIVE', t_frame='ACTIVE', t_stroke='SELECT'):
    '''print the pressure of targeted strokes'''
    print('Pressure per stroke')
    for s in strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke):
        print(['{:.3f}'.format(p.pressure) for p in s.points])

def thin_stroke_tips(tip_len=5, middle=0, t_layer='ACTIVE', t_frame='ACTIVE', t_stroke='SELECT'):
    '''Thin tips of strokes on target layers/frames/strokes defaut (active layer > active frame > selected strokes)'''
    for l in get_layers(target=t_layer):
        for f in get_frames(l, target=t_frame):
            for s in get_strokes(f, target=t_stroke):
                abs_thinner_tip(s, tip_len=5, middle=0)

def thin_stroke_tips_percentage(tip_len=30, variance=0, t_layer='ALL', t_frame='ACTIVE', t_stroke='SELECT'):
    '''Thin tips of strokes on target layers/frames/strokes defaut (active layer > active frame > selected strokes)'''
    for s in strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke):
        reshape_rel_thinner_tip_percentage(s, tip_len=tip_len, variance=variance)

## -- Trim / Progressive erase

def trim_tip_point(endpoint=True):
    '''endpoint : delete last point, else first point'''
    last = bpy.context.object.data.layers.active.active_frame.strokes[-1]
    if len(last.points) > 2:# erase point
        if endpoint:
            last.points.pop(index=-1)#pop default
        else:
            last.points.pop(index=0)
    else:# erase lines
        for i in range( len(last.points) ):
            last.points.pop()
        bpy.context.object.data.layers.active.active_frame.strokes.remove(last)

#TODO - preserve tip triming (option or another func), (need a "detect fade" function to give at with index the point really start to fade and offset that) 

def delete_stroke(strokes, s):
    for i in range(len(s.points)):
        s.points.pop()#pop all point to update viewport
    strokes.remove(s)

def backup_point_as_dic(p):
    '''backup point as dic (same layer, no parent handling)'''
    attrlist = ['co', 'pressure', 'select', 'strength', 'uv_factor', 'uv_rotation']
    pdic = {}
    for attr in attrlist:
        # pdic = getattr(p, attr)
        pdic[attr] = getattr(p, attr)
    return pdic

def backup_stroke(s, ids=None):
    '''backup given points index if ids pass'''
    stroke_attr_list = ('display_mode', 'draw_cyclic', 'end_cap_mode', 'gradient_factor', 'gradient_shape', 'groups', 'is_nofill_stroke', 'line_width', 'material_index', 'start_cap_mode' )#
    sdic = {}
    for att in stroke_attr_list:
        sdic[att] = getattr(s, att)
    points = []
    if ids:
        for pid in ids:
            points.append(backup_point_as_dic(s.points[pid]))
    else:
        for p in s.points:
            points.append(backup_point_as_dic(p))
    sdic['points'] = points
    return sdic

def pseudo_subdiv(a, b, c, d):
    A = location_to_region(a['co'])
    B = location_to_region(b['co'])
    C = location_to_region(c['co'])
    D = location_to_region(d['co'])

    ABl = vector_len_from_coord(A, B)
    CDl = vector_len_from_coord(C, D)
    average_sampling_dist = mean(ABl, CDl)#in automatic mode should respect this average distance.

    #determine where prolonged vector AB-> cross prolonged vector CD-> (problem : if bad angle...)
    # lets subdivide two last stroke instead.


def to_straight_line(s, keep_points=True, influence=100, straight_pressure=True):
    '''
    keep points : if false only start and end point stay
    straight_pressure : (not available with keep point) take the mean pressure of all points and apply to stroke.
    '''
    
    p_len = len(s.points)
    if p_len <= 2: # 1 or 2 points only, cancel
        return

    if not keep_points:
        if straight_pressure: mean_pressure = mean([p.pressure for p in s.points])#can use a foreach_get but might not be faster.
        for i in range(p_len-2):
            s.points.pop(index=1)
        if straight_pressure:
            for p in s.points:
                p.pressure = mean_pressure

    else:
        A = s.points[0].co
        B = s.points[-1].co
        ab_dist = vector_len_from_coord(A,B)
        full_dist = get_stroke_length(s)
        dist_from_start = 0.0
        coord_list = []
        
        for i in range(1, p_len-1):#all but first and last
            dist_from_start += vector_len_from_coord(s.points[i-1],s.points[i])
            ratio = dist_from_start / full_dist
            # dont apply directly (change line as we measure it in loop)
            coord_list.append( point_from_dist_in_segment_3d(A, B, ratio) )
        
        # apply change
        for i in range(1, p_len-1):
            #s.points[i].co = coord_list[i-1]#direct super straight 100%
            s.points[i].co = point_from_dist_in_segment_3d(s.points[i].co, coord_list[i-1], influence / 100)


#without reduce (may be faster)
def gp_select_by_angle(tol, invert=False):
    #print(strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke))
    for s in selected_strokes():
        pnum = len(s.points)
        if pnum >= 3:#need at least 3 points to calculate angle
            for i in range(pnum-2):#skip two last -2
                a = location_to_region(s.points[i].co)
                b = location_to_region(s.points[i+1].co)
                c = location_to_region(s.points[i+2].co)
                ab = b-a
                bc = c-b
                
                #test if fasted with numpy than built in angle method !!
                angle = get_angle(ab,bc)
                # direct_angle = degrees(ab.angle(bc))#angle_signed
                # if abs(angle) > tol:
                s.points[i+1].select = (abs(angle) > tol) ^ invert

def gp_select_by_angle_reducted(tol, invert=False):
    #print(strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke))
    for s in selected_strokes():
        keys = []
        pnum = len(s.points)
        if pnum >= 3:#need at least 3 points to calculate angle
            suite = []
            for i in range(pnum-2):#skip two last -2
                a = location_to_region(s.points[i].co)
                b = location_to_region(s.points[i+1].co)
                c = location_to_region(s.points[i+2].co)
                ab = b-a
                bc = c-b
                
                angle = get_angle(ab,bc)#test if fasted with numpy than built in angle method !
                # direct_angle = degrees(ab.angle(bc))#angle_signed
                absangle = abs(angle)

                if absangle > tol:
                    suite.append([i+1, absangle])
                else:
                    if suite:#suite has ended
                        #first element of decreasing filtered list, then index of the points
                        keys.append(sorted(suite, key=lambda x: x[1], reverse=True)[0][0])
                        suite = []
                
            sel_list = [(i in keys) ^ invert for i in range(pnum)]
            s.points.foreach_set('select', sel_list)
            # s.points[i+1].select = abs(angle) > tol
                    
                #calculate vector from current and next and store only "key" points:


### straight by slice and slices getters for polygonize

def straight_stroke_slice(s, influence=100, slices=[], reduce=False, delete=False):
    if not slices:
        slices = [0, len(s.points)]

    if delete:# remove points within slices range (influence is irelevant)
        
        if reduce and isinstance(slices[-1], list) and slices[-1][0]+1 < slices[-1][1]:
            # with reduce on, delete mode often delete last point... substract last slice by one if possible and if reduce is passed
            slices[-1][1] = slices[-1][1] - 1

        for sl in reversed(slices):
            # print(sl)
            for pid in reversed(range(sl[0]+1,sl[1])):#sl[1]+1 ?
                s.points.pop(index=pid)
        return

    for sl in slices:
        s_id, e_id = sl[0], sl[1]
        if e_id >= len(s.points):
            # print('len(s.points): ', len(s.points))
            # print('e_id: ', e_id)
            e_id = len(s.points) - 1

        A = s.points[s_id].co
        B = s.points[e_id].co
        # ab_dist = vector_len_from_coord(A,B)
        full_dist = sum( [vector_len_from_coord(s.points[i],s.points[i+1]) for i in range(s_id, e_id)] )
        dist_from_start = 0.0
        coord_list = []
        
        for i in range(s_id+1, e_id):#all but first and last
            dist_from_start += vector_len_from_coord(s.points[i-1],s.points[i])
            ratio = dist_from_start / full_dist
            # dont apply directly (change line as we measure it in loop)
            coord_list.append( point_from_dist_in_segment_3d(A, B, ratio) )
        
        for count, i in enumerate(range(s_id+1, e_id)):#e_id
            #s.points[i].co = coord_list[i-1]#direct super straight 100%
            s.points[i].co = point_from_dist_in_segment_3d(s.points[i].co, coord_list[count], influence / 100)
    
                

def get_points_id_by_reduced_angles(s, tol):
    #print(strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke))
    keys = []
    pnum = len(s.points)
    if pnum >= 3:#need at least 3 points to calculate angle
        suite = []
        for i in range(pnum-2):#skip two last -2
            a = location_to_region(s.points[i].co)
            b = location_to_region(s.points[i+1].co)
            c = location_to_region(s.points[i+2].co)
            ab = b-a
            bc = c-b
            
            angle = get_angle(ab,bc)#test if fasted with numpy than built in angle method !
            # direct_angle = degrees(ab.angle(bc))#angle_signed
            absangle = abs(angle)

            if absangle > tol:
                suite.append([i+1, absangle])
            else:
                if suite:#suite has ended
                    #first element of decreasing filtered list, then index of the points
                    keys.append(sorted(suite, key=lambda x: x[1], reverse=True)[0][0])
                    suite = []
        if len(keys) > 1:
            keys.insert(0, 0)#add first and last
            keys.append(pnum)
            pairs = [[keys[i], keys[i+1]] for i in range(len(keys)-1)]
            return pairs

def get_points_id_by_angles(s, tol, invert=False):
    pnum = len(s.points)
    pairs = []
    prev = False
    added = 0
    if pnum >= 3:#need at least 3 points to calculate angle
        for i in range(pnum-2):#skip two last -2
            a = location_to_region(s.points[i].co)
            b = location_to_region(s.points[i+1].co)
            c = location_to_region(s.points[i+2].co)
            ab = b-a
            bc = c-b
            angle = get_angle(ab,bc)
            # s.points[i+1].select = (abs(angle) > tol) ^ invert
            if not (abs(angle) > tol) ^ invert:#check without not and invert after if needed...
                added +=1
                if not prev:
                    start = i+1
                prev = True
            else:
                if prev:
                    pairs.append([start, i+1])
                    prev = False

        if added > 1:
            return pairs

def gp_polygonize(s, tol, influence=100, reduce=True, delete=False):#, t_layer='ALL', t_frame='ACTIVE', t_stroke='SELECT'
    #print(strokelist(t_layer=t_layer, t_frame=t_frame, t_stroke=t_stroke))
    if reduce:
        pairs = get_points_id_by_reduced_angles(s, tol)
    else:
        pairs = get_points_id_by_angles(s, tol)
    
    # print('pairs: ', pairs)
    if pairs:
        straight_stroke_slice(s, influence, pairs, reduce=reduce, delete=delete)


def guess_join(same_material=True, proximity_tolerance=0.01, start_point_tolerance=6):
    '''
    start_point_tolerance to 0 means only first point is evaluated on last stroke
    proximity_tolerance set the distance under wich points of other lines are "joinable"
    Return error if no points are found close enough.
    '''
    #get last stroke
    last = bpy.context.object.data.layers.active.active_frame.strokes[-1]
    #strokelist(t_layer='ACTIVE', t_frame='ACTIVE', t_stroke='ALL')
    
    # fpt = last.points[0]
    
    #get other strokes of current layer
    found = False
    if same_material:
        pool = [s for s in bpy.context.object.data.layers.active.active_frame.strokes[:-1] if s.material_index == last.material_index]
    else:
        pool = bpy.context.object.data.layers.active.active_frame.strokes[:-1]

    #clamp
    start_point_tolerance = len(last.points)-1 if start_point_tolerance >= len(last.points) else start_point_tolerance
    closes = []
    ct = 0
    for s in pool:
        for pid, p in enumerate(s.points):
            for i in range(1 + start_point_tolerance):
                if checkalign(location_to_region(p.co), location_to_region(last.points[i].co), tol=proximity_tolerance):#2D check #tol=0.01
                    # print(f'{i} > {pid}')
                    ct+=1
                    found = True
                    ### OLD :0 point index, 1 towards end or not (true false), 2 coordinate, 3 point obj, 4 stroke obj, 5 disance from reference point, index of point on last.
                    ### 0 point index, 1 point, 2 stroke, 3 distance from reference point, 4 ref point index 
                    closes.append([pid, p, s, vector_len_from_coord(last.points[i], p) , i])
        
        # if found:#Dont check for another close stroke that might overlap. (maybe change that later)
        #     break
    
    
    if found :
        print(f'{ct} close points found')
        closes.sort(key=lambda x: x[3])#filter to find point that has the closest distance accross athorized points on the last lines.
        closest = closes[0]#list element
        close_stroke = closest[2]#Target stroke
        
        #check if crossed, if it is do an intersection join thing.
        # print('closest: ', closest)

        start_point_index = closest[4]
        # last.points[start_point_index].select = True#Dbg
        start_id = 0
        end_id = len(close_stroke.points)-1

        from_end_tip = True        
        if closest[0] / len(closest[2].points) >= 0.5:#near end
            end_point_index = clamp(closest[0]-1, start_id, end_id)#point before detected point
            
            slist = [i for i in range(0, end_point_index)]
        
        else:#near start
            from_end_tip = False
            end_point_index = clamp(closest[0]+1, start_id, end_id)#point after detected point
            
            slist = [end_id-i for i in range(end_id-end_point_index)]# ex:[9,8,7,4,3,2]
        
        llist = [i for i in range(start_point_index, len(last.points))]

        # close_stroke.points[end_point_index].select = True#Dbg
        # print('len(close_stroke.points): ', len(close_stroke.points))
        # print('len(last.points): ', len(last.points))

        stardic = [backup_point_as_dic(close_stroke.points[i]) for i in slist]
        lastdic = [backup_point_as_dic(last.points[i]) for i in llist]


        # For smoothness sake, place a "subdivided" point between the tww according to point orientation
        # Will only work in persp view, disable.
        subdiv_points = pseudo_subdiv(stardic[-2], stardic[-1], lastdic[0], lastdic[1])
        all_points_dic = stardic + lastdic
        
        ### Create stroke
        
        ns = bpy.context.object.data.layers.active.active_frame.strokes.new()
        for s_attr in ('display_mode', 'draw_cyclic', 'end_cap_mode', 'gradient_factor', 'gradient_shape', 'line_width', 'material_index', 'start_cap_mode' ):
            ## readonly : 'groups', 'is_nofill_stroke',
            setattr(ns, s_attr, getattr(last,s_attr))#same stroke settings as last stroke

        ## add all points
        ns.points.add(len(all_points_dic))
        # print('all_points_dic: ', all_points_dic)
        for i, pdic in enumerate(all_points_dic):
            # print('pdic: ', pdic)
            for k, v in pdic.items():
                setattr(ns.points[i], k, v)

        ## delete old stroke
        delete_stroke(bpy.context.object.data.layers.active.active_frame.strokes, close_stroke)
        delete_stroke(bpy.context.object.data.layers.active.active_frame.strokes, last)
        
    else:
        return 'No close stroke found to join last.\nTry increse the tolerance and check if there is no depth offset from your point of view'


# TODO make a function to join the two last strokes (best would be with a sampled interpolated curve between the last and first point... hard)