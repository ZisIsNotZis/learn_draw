"""Dispatch the implemented flat recipes; locks retain their editable strip geometry."""
from .geometry import lock_rows
from .scenery import DEFAULT_DEPTH, DEFAULT_LENGTH, KINDS


def component_data(node,canvas):
    if node['kind']=='head':
        from .head import head_data
        return head_data(node,canvas)
    from .scenery import scenery_data
    return scenery_data(node,canvas)


def support(node,canvas):
    kind=node['kind']
    root_y=lock_rows(node,canvas)[0].left[1] if kind=='hair-lock' else component_data(node,canvas).center[1]
    scale=node.get('length',DEFAULT_LENGTH.get(kind,.55 if kind=='head' else .68))*min(canvas)
    return root_y,scale,node.get('depth',DEFAULT_DEPTH.get(kind,0))
