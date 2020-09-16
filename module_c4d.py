#!usr/bin/python
# -*- coding: utf-8 -*-

import c4d

context_doc = c4d.documents.GetActiveDocument()
context_obj = context_doc.GetActiveObject()

ID_DIRS = [c4d.VECTOR_X, c4d.VECTOR_Y, c4d.VECTOR_Z]
ID_TYPES = [c4d.ID_BASEOBJECT_REL_POSITION,
            c4d.ID_BASEOBJECT_REL_ROTATION,
            c4d.ID_BASEOBJECT_REL_SCALE]

_MATRIX_CV = c4d.Matrix(v2=c4d.Vector(0, 0, 1), v3=c4d.Vector(0, 1, 0))


class Matrix(object):

    def __init__(self, elements=None):
        """

        :type elements: Union[list, c4d.Matrix]
        :param elements:
        """
        if elements is None:
            self.__matrix = c4d.Matrix()
        elif type(elements) is c4d.Matrix:
            self.__matrix = c4d.Matrix(elements)
        else:
            if len(elements) < 12:
                off = c4d.Vector()
            else:
                # Convert to CM
                off = c4d.Vector(elements[-3] * 100,
                                 elements[-2] * 100,
                                 elements[-1] * 100)
            v1 = c4d.Vector(elements[0], elements[1], elements[2])
            v2 = c4d.Vector(elements[3], elements[4], elements[5])
            v3 = c4d.Vector(elements[6], elements[7], elements[8])
            # Convert to LHS
            self.__matrix = _MATRIX_CV * c4d.Matrix(off, v1, v2, v3) * _MATRIX_CV

    def __mul__(self, other):
        return Matrix(self.__matrix * other.__matrix)

    def __repr__(self):
        return self.__matrix.__repr__()

    def convert_to_list(self):
        """

        :return:
        :rtype: list
        """
        output = []
        # Convert to RHS
        tmp_matrix = _MATRIX_CV * self.__matrix * _MATRIX_CV
        # Convert to M
        for i in [tmp_matrix.v1,
                  tmp_matrix.v2,
                  tmp_matrix.v3,
                  tmp_matrix.off / 100]:
            for j in range(3):
                output.append(i[j])
        return output

    def invert(self):
        return Matrix(self.__matrix.__invert__())

    def get(self):
        return self.__matrix


def _search_obj(name, obj):
    str_a = obj.GetName().decode('utf-8')
    if str_a == name:
        return obj
    for i in obj.GetChildren():
        result = _search_obj(name, i)
        if result is not None:
            return result
    return None


class BaseObject(object):

    def __init__(self, obj):
        """

        :type obj: c4d.BaseObject
        :param obj:
        """
        self.__object = obj

    def get_matrix(self, frame):
        # F**k U Cinema 4D!
        transform = [
            c4d.Vector(self.__object.GetRelPos()),
            c4d.Vector(self.__object.GetRelRot()),
            c4d.Vector(self.__object.GetRelScale())
        ]
        for track in self.__object.GetCTracks():
            i_type = ID_TYPES.index(track.GetDescriptionID()[0].id)
            i_dir = ID_DIRS.index(track.GetDescriptionID()[1].id)
            fps = get_fps()
            transform[i_type][i_dir] = track.GetCurve().GetValue(
                c4d.BaseTime(frame, fps), fps
            )
        return Matrix(c4d.utils.MatrixMove(transform[0])
                      * c4d.utils.HPBToMatrix(transform[1],
                                              self.__object.GetRotationOrder())
                      * c4d.utils.MatrixScale(transform[2]))

    def set_matrix(self, matrix, frame):
        """

        :type frame: int
        :param frame:
        :type: Matrix
        :param matrix:
        :return:
        """
        transform = [
            matrix.get().off,
            c4d.utils.MatrixToHPB(matrix.get(), self.__object.GetRotationOrder()),
            matrix.get().GetScale()
        ]
        for i_type in range(3):
            for i_dir in range(3):
                desc_id = c4d.DescID(
                    c4d.DescLevel(ID_TYPES[i_type], c4d.DTYPE_VECTOR, 0),
                    c4d.DescLevel(ID_DIRS[i_dir], c4d.DTYPE_REAL, 0)
                )
                track = self.__object.FindCTrack(desc_id)
                if track is None:
                    track = c4d.CTrack(self.__object, desc_id)
                    self.__object.InsertTrackSorted(track)
                curve = track.GetCurve()
                key = curve.AddKey(c4d.BaseTime(frame, get_fps()))['key']
                if key is None:
                    print('Error: Failed to add keys!')
                    continue
                track.FillKey(context_doc, self.__object, key)
                key.SetValue(curve, transform[i_type][i_dir])

    # Todo: get/set timeline
    def get_attr(self, id_attr):
        """

        :type id_attr: int
        :param id_attr:
        :return:
        :rtype: Any
        """
        return self.__object[c4d.ID_USERDATA, id_attr]

    def set_attr(self, id_attr, value):
        """

        :type id_attr: int
        :param id_attr:
        :type value: Any
        :param value:
        :return:
        """
        self.__object[c4d.ID_USERDATA, id_attr] = value

    @classmethod
    def search_obj(cls, name, obj=context_obj):
        """

        :type name: str
        :type obj: c4d.BaseObject
        :param name: Name of the object.
        :param obj: Parent of the object.
        :return: Object.
        :rtype: BaseObject
        """
        return cls(_search_obj(name, obj))


def get_fps():
    return context_doc.GetFps()


# Todo: loop time (previous)
def get_frames(r_type=range):
    fps = get_fps()
    if r_type == range:
        return range(context_doc.GetMinTime().GetFrame(fps),
                     context_doc.GetMaxTime().GetFrame(fps) + 1)
    else:
        return [context_doc.GetMinTime().GetFrame(fps),
                context_doc.GetMaxTime().GetFrame(fps)]


def set_frame(frame):
    # Todo: not used
    # context_doc.SetTime(c4d.BaseTime(float(frame) / get_fps()))
    pass


def init_settings(frame_start, frame_end, fps):
    context_doc.SetFps(fps)
    context_doc.SetMinTime(c4d.BaseTime(frame_start, fps))
    context_doc.SetMaxTime(c4d.BaseTime(frame_end, fps))


def add_event():
    c4d.EventAdd()


def test_print():
    from sys import version_info as py_ver_info
    py_ver = py_ver_info.major
    print('You are using Python {}.x.'.format(py_ver))
    if py_ver != 2:
        print('Warning: It is not supported in C4D.')
        print('         You should use Python 2 instead.')


if __name__ == '__main__':
    test_print()
