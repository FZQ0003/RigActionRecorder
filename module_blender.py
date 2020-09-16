#!usr/bin/python3
# -*- coding: utf-8 -*-

import bpy
import mathutils

context_obj = bpy.context.object
context_doc = bpy.context.scene


class Matrix(object):

    def __init__(self, elements=None):
        """

        :type elements: list
        :param elements:
        """
        if type(elements) is mathutils.Matrix:
            self.__matrix = elements.copy()
        else:
            self.__matrix = mathutils.Matrix()
            if elements is not None:
                for i in range(len(elements)):
                    self.__matrix[i % 3][i // 3] = elements[i]

    def __mul__(self, other):
        return Matrix(self.__matrix @ other.__matrix)

    def __repr__(self):
        return self.__matrix.__repr__()

    def convert_to_list(self):
        """

        :return:
        :rtype: list
        """
        output = []
        for i in range(12):
            output.append(self.__matrix[i % 3][i // 3])
        return output

    def invert(self):
        return Matrix(self.__matrix.inverted())

    def get(self):
        return self.__matrix


class BaseObject(object):

    def __init__(self, obj):
        """

        :type obj: Union[bpy.types.Object, bpy.types.PoseBone]
        :param obj:
        """
        self.__object = obj

    def get_matrix(self, frame):
        transform = [
            self.__object.location.copy(),
            self.__object.rotation_euler.copy(),
            self.__object.scale.copy()
        ]
        if type(self.__object) is bpy.types.PoseBone:
            curves = self.__object.id_data.animation_data.action.fcurves
            base_path = self.__object.path_from_id() + '.'
        else:
            curves = self.__object.animation_data.action.fcurves
            base_path = ''
        list_path = ['location', 'rotation_euler', 'scale']
        for str_path in list_path:
            tmp_index = [0, 1, 2]
            for curve in curves:
                if curve.data_path == base_path + str_path \
                        and curve.array_index in tmp_index:
                    tmp_index.remove(curve.array_index)
                    transform[list_path.index(str_path)][curve.array_index] \
                        = curve.evaluate(frame)
                if len(tmp_index) < 1:
                    break
        tmp_rot = transform[1].to_matrix()
        tmp_rot.resize_4x4()
        tmp_size = mathutils.Matrix.Diagonal(transform[2])
        tmp_size.resize_4x4()
        return Matrix(mathutils.Matrix.Translation(transform[0])
                      @ tmp_rot @ tmp_size)

    def set_matrix(self, matrix, frame):
        """

        :type frame: int
        :param frame:
        :type: Matrix
        :param matrix:
        :return:
        """
        # F**k U blender!
        rot_mode = self.__object.rotation_mode
        # Todo: extra rot orders
        if rot_mode in ['QUATERNION', 'AXIS_ANGLE']:
            self.__object.rotation_mode = 'XYZ'
            rot_mode = 'XYZ'
        self.__object.location = matrix.get().to_translation()
        self.__object.rotation_euler = matrix.get().to_euler(rot_mode)
        self.__object.scale = matrix.get().to_scale()
        for str_path in ['location', 'rotation_euler', 'scale']:
            self.__object.keyframe_insert(data_path=str_path, frame=frame)

    # Todo: get/set timeline
    def get_attr(self, id_attr):
        """

        :type id_attr: str
        :param id_attr:
        :return:
        :rtype: Any
        """
        return self.__object[id_attr]

    def set_attr(self, id_attr, value):
        """

        :type id_attr: str
        :param id_attr:
        :type value: Any
        :param value:
        :return:
        """
        self.__object[id_attr] = value

    @classmethod
    def search_obj(cls, name, obj=context_obj):
        """

        :type name: str
        :type obj: bpy.types.Object
        :param name: Name of the object.
        :param obj: Parent of the object. (Not Used)
        :return: Object.
        :rtype: BaseObject
        """
        # Todo: PoseBone & Object
        return cls(context_obj.pose.bones.get(name, None))


def get_fps():
    render = context_doc.render
    return render.fps / render.fps_base


# Todo: previous frame
def get_frames(r_type=range):
    if r_type == range:
        return range(context_doc.frame_start, context_doc.frame_end + 1)
    else:
        return [context_doc.frame_start, context_doc.frame_end]


def set_frame(frame):
    context_doc.frame_current = frame


def init_settings(frame_start, frame_end, fps):
    context_doc.frame_start = frame_start
    context_doc.frame_end = frame_end
    context_doc.render.fps = fps
    context_doc.render.fps_base = 1


def add_event():
    pass


def test_print():
    from sys import version_info as py_ver_info
    py_ver = py_ver_info.major
    print('You are using Python {}.x.'.format(py_ver))
    if py_ver != 3:
        print('Warning: It is not supported in Blender.')
        print('         You should use Python 3 instead.')


if __name__ == '__main__':
    test_print()
