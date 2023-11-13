"""
Remote debugging support.

This addon allows you to use a remote Python debugger with PyCharm, PyDev and
possibly other IDEs. As it is, without modification, it only supports PyCharm,
but it may work by pointing it at a similar egg file shipped with PyDev.

Before using, point the addon to your pycharm-debug-py3k.egg file in the
addon preferences screen.

For more information on how to use this addon, please read my article at
http://code.blender.org/2015/10/debugging-python-code-with-pycharm/
"""

bl_info = {
    'name': 'Remote debugger',
    'author': 'Sybren A. Stüvel',
    'version': (0, 5, 0),
    'blender': (3, 0, 0),
    'location': 'Press [F3] (in Blender 2.80-3.00) or [Space] (in Blender 2.79) and then search for "debugger"',
    'category': 'Development',
}

import bpy
import os.path
from bpy.types import AddonPreferences
from bpy.props import StringProperty


# Get references to all property definition functions in bpy.props,
# so that they can be used to replace 'x = IntProperty()' to 'x: IntProperty()'
# dynamically when working on Blender 2.80+
__all_prop_funcs = {
    getattr(bpy.props, propname)
    for propname in dir(bpy.props)
    if propname.endswith('Property')
}

def convert_properties(class_):
    """Class decorator to avoid warnings in Blender 2.80+
    This decorator replaces property definitions like this:
        someprop = bpy.props.IntProperty()
    to annotations, as introduced in Blender 2.80:
        someprop: bpy.props.IntProperty()
    No-op if running on Blender 2.79 or older.
    """

    if bpy.app.version < (2, 80):
        return class_

    if not hasattr(class_, '__annotations__'):
        class_.__annotations__ = {}

    for name, value in class_.__dict__.items():
        # This is a property definition, add annotation for it.
        if name in ("eggpath", "pydevpath"):
            class_.__annotations__[name] = value

    return class_


def addon_preferences(context):
    try:
        preferences = context.preferences
    except AttributeError:
        # Old (<2.80) location of user preferences
        preferences = context.user_preferences

    return preferences.addons[__name__].preferences


@convert_properties
class DebuggerAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    eggpath = StringProperty(
        name='Path of the PyCharm egg file',
        description='Make sure you select the py3k egg',
        subtype='FILE_PATH',
        default='pycharm-debug-py3k.egg'
    )

    pydevpath = StringProperty(
        name='Path of the PyDev pydevd.py file',
        subtype='FILE_PATH',
        default='pydevd.py'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'pydevpath')
        layout.prop(self, 'eggpath')
        layout.label(text='Make sure you select the egg for Python 3.x: pycharm-debug-py3k.egg ')


class DEBUG_OT_connect_debugger_pycharm(bpy.types.Operator):
    bl_idname = 'debug.connect_debugger_pycharm'
    bl_label = 'Connect to remote PyCharm debugger'
    bl_description = 'Connects to a PyCharm debugger on localhost:1090'

    def execute(self, context):
        import sys

        addon_prefs = addon_preferences(context)
        eggpath = os.path.abspath(addon_prefs.eggpath)

        if not os.path.exists(eggpath):
            self.report({'ERROR'}, 'Unable to find debug egg at %r. Configure the addon properties '
                                   'in the User Preferences menu.' % eggpath)
            return {'CANCELLED'}

        if not any('pycharm-debug' in p for p in sys.path):
            sys.path.append(eggpath)

        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=1090, stdoutToServer=True, stderrToServer=True,
                        suspend=False)

        return {'FINISHED'}


class DEBUG_OT_connect_debugger_pydev(bpy.types.Operator):
    bl_idname = 'debug.connect_debugger_pydev'
    bl_label = 'Connect to remote PyDev debugger'
    bl_description = 'Connects to a PyDev debugger on localhost:5678'

    def execute(self, context):
        import sys

        addon_prefs = addon_preferences(context)
        pydevpath = os.path.abspath(addon_prefs.pydevpath)

        if not os.path.exists(pydevpath):
            self.report({'ERROR'}, 'Unable to find pydevd.py at %r. Configure the addon properties '
                                   'in the User Preferences menu.' % pydevpath)
            return {'CANCELLED'}

        dirname = os.path.dirname(pydevpath)
        basename = os.path.basename(dirname)
        if not any(basename in p for p in sys.path):
            sys.path.append(dirname)

        import pydevd
        pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True,
                        suspend=False)

        return {'FINISHED'}


classes = (
    DEBUG_OT_connect_debugger_pycharm,
    DEBUG_OT_connect_debugger_pydev,
    DebuggerAddonPreferences,
)

def DEBUG_OT_connect_debugger_pycharm_menu(self, context):
    self.layout.operator(DEBUG_OT_connect_debugger_pycharm.bl_idname, text=DEBUG_OT_connect_debugger_pycharm.bl_label)

def DEBUG_OT_connect_debugger_pydev_menu(self, context):
    self.layout.operator(DEBUG_OT_connect_debugger_pydev.bl_idname, text=DEBUG_OT_connect_debugger_pydev.bl_label)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_view.append(DEBUG_OT_connect_debugger_pycharm_menu)
    bpy.types.VIEW3D_MT_view.append(DEBUG_OT_connect_debugger_pydev_menu)


def unregister():
    bpy.types.VIEW3D_MT_view.remove(DEBUG_OT_connect_debugger_pydev_menu)
    bpy.types.VIEW3D_MT_view.remove(DEBUG_OT_connect_debugger_pycharm_menu)
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == '__main__':
    register()
