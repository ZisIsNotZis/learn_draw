"""Dispatch the implemented flat recipes; locks retain their editable strip geometry."""
from .geometry import lock_rows,outline
from .scenery import DEFAULT_DEPTH, DEFAULT_LENGTH, KINDS


def component_data(node,canvas):
    if node['kind']=='head':
        from .head import head_data
        return head_data(node,canvas)
    if node['kind']=='hand':
        from .hand import hand_data
        return hand_data(node,canvas)
    from .scenery import scenery_data
    return scenery_data(node,canvas)


def component_outline(node,canvas):
    return outline(lock_rows(node,canvas)) if node['kind']=='hair-lock' else list(component_data(node,canvas).outline)


def support(node,canvas):
    kind=node['kind']
    root_y=lock_rows(node,canvas)[0].left[1] if kind=='hair-lock' else component_data(node,canvas).center[1]
    if kind=='hand':
        from .hand import DEFAULT_LENGTH as hand_length
        default_length=hand_length
    else:
        default_length=DEFAULT_LENGTH.get(kind,.55 if kind=='head' else .68)
    scale=node.get('length',default_length)*min(canvas)
    return root_y,scale,node.get('depth',DEFAULT_DEPTH.get(kind,0))


def depth_bounds(node,canvas):
    root_y,scale,depth=support(node,canvas)
    values=[depth+node.get('depth_slope',0)*(p[1]-root_y)/scale for p in component_outline(node,canvas)]
    return min(values),max(values)
