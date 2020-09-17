#!usr/bin/python3
# -*- coding: utf-8 -*-

import json
import sys

# Paste your script dirname here. use "\\" instead of "\".
SCRIPT_DIR = 'C:\\Users\\30743\\PycharmProjects\\RigActionRecorder'
# enum of ['get_action', 'set_action']
COMMAND = 'get_action'

if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

try:
    import module_c4d as mod

    PLATFORM = 'c4d'
except ImportError:
    import module_blender as mod

    PLATFORM = 'blender'

try:
    from importlib import reload
except ImportError:
    pass

reload(mod)


def numlist_convert(numlist, indexes):
    """

    :type numlist: list
    :param numlist:
    :type indexes: Union[list, int, None]
    :param indexes:
    :return:
    :rtype: Union[list, float]
    """
    if numlist is None or indexes is None:
        return numlist
    elif type(indexes) is int:
        indexes = [indexes]
    if len(numlist) == len(indexes):
        result = [1.0, 0.0, 0.0,
                  0.0, 1.0, 0.0,
                  0.0, 0.0, 0.1,
                  0.0, 0.0, 0.0]
        for i in indexes:
            result[i] = numlist[indexes.index(i)]
    else:
        result = []
        for i in indexes:
            result.append(numlist[i])
    if len(result) == 1:
        return result[0]
    else:
        return result


class DataJson(object):

    def __init__(self, path=None):
        # protected
        self._data = {}
        self._version = 0.1
        # public
        self.isvalid = False
        if path is not None:
            self.read_text(path)

    def read_text(self, path):
        """

        :type path: str
        :param path:
        :return:
        """
        with open(path, 'rb') as f:
            self._data = json.load(f)
        if self._data['data_version'] == self._version:
            self.isvalid = True
        else:
            print('Error: Check version failed.')
            self.isvalid = False

    def save_text(self, path):
        """

        :type path: str
        :param path:
        :return:
        """
        with open(path, 'w') as f:
            json.dump(self._data, f, sort_keys=True, indent=2)


class RigProp(DataJson):

    def __init__(self, path=None):
        # protected
        self._rig = {}
        super(RigProp, self).__init__(path)

    def list_rigs(self):
        """

        :return:
        :rtype: list
        """
        output_list = []
        for data_rig in self._data['rigs']:
            if data_rig['model_type'] == PLATFORM:
                if type(data_rig['version']) is not list:
                    data_rig['version'] = [data_rig['version']]
                output_list.append([data_rig['id'], data_rig['version']])
        # for i in output_list:
        #     print(i[0], i[1])
        return output_list

    def set_rig(self, id_rig):
        """

        :type id_rig: str
        :param id_rig:
        :return:
        :rtype: bool
        """
        for data_rig in self._data['rigs']:
            if data_rig['model_type'] == PLATFORM and data_rig['id'] == id_rig:
                self._rig = data_rig['object']
                return True
        print('Error: No rigs matched.')
        return False

    def list_objects(self):
        """

        :return:
        :rtype: list
        """
        output_list = []
        for obj in self._rig:
            output_list.append(obj['id'])
        return output_list

    def get_object(self, id_obj):
        """

        :type id_obj: str
        :param id_obj:
        :return:
        :rtype: dict
        """
        for obj in self._rig:
            if obj['id'] == id_obj:
                return obj
        return {}

    def __iter__(self):
        return self._rig


class Output(DataJson):

    def __init__(self, path=None):
        super(Output, self).__init__(path)
        if path is None:
            self._data['data_version'] = 0.2
            self._data['rigs'] = []
            self.write_settings()
        else:
            self.read_settings()

    def get_rig_data(self, name=''):
        for rig in self._data.get('rigs', []):
            if name == rig.get('name', ''):
                return rig
        return {}

    def append_data(self, input_data):
        """

        :type input_data: dict
        :param input_data:
        :return:
        """
        self._data['rigs'].append(input_data.copy())

    def get_transform(self, id_obj, frame):
        """

        :type frame: int
        :param frame:
        :type id_obj: str
        :param id_obj:
        :return:
        :rtype: Union[list, int]
        """
        for obj in self.get_data():
            if obj['id'] == id_obj:
                return obj.get('%04d' % frame, None)
        return None

    def read_settings(self):
        project = self._data.get('project', None)
        if project is not None:
            mod.init_settings(
                project['frame_range'][0],
                project['frame_range'][1],
                project['fps']
            )

    def write_settings(self):
        self._data['project'] = {
            'frame_range': mod.get_frames(list),
            'fps': mod.get_fps()
        }

    def __iter__(self):
        return self._data.get('rigs', [])


path_prop = SCRIPT_DIR + '\\prop.json'
path_output = SCRIPT_DIR + '\\output.json'

data = RigProp(path_prop)
data.list_rigs()
if PLATFORM == 'c4d':
    data.set_rig('varcade')
else:
    data.set_rig('varcade-bl')


# Use SI (eg. use "m" not "cm") & RHS.
def get_action():
    output = Output()

    # for id_obj in data.list_objects():
    for data_obj in data:
        # data_obj = data.get_object(id_obj)
        id_obj = data_obj['id']
        if data_obj.get('readable', True):
            local_coord = mod.Matrix(data_obj.get('local_coord', None))
            obj = mod.BaseObject.search_obj(data_obj['name'], mod.context_obj)

            # Todo: other args -> matrix
            # Todo: get attribute
            # M_Output = ML * LC * M_Input * LC^(-1) * MR
            matrix_left = (mod.Matrix(data_obj.get('mat_left', None))
                           * local_coord)
            matrix_right = (local_coord.invert()
                            * mod.Matrix(data_obj.get('mat_right', None)))

            output_data = {'id': id_obj}
            for i in mod.get_frames(range):
                mod.set_frame(i)
                output_data['%04d' % i] = numlist_convert(
                    (matrix_left
                     * obj.get_matrix(i)
                     * matrix_right).convert_to_list(),
                    data_obj.get('indexes', None)
                )
            output.append_data(output_data)

    output.save_text(path_output)


def set_action():
    output = Output(path_output)

    # for id_obj in data.list_objects():
    for data_obj in data:
        # data_obj = data.get_object(id_obj)
        id_obj = data_obj['id']
        if data_obj.get('readable', True):
            local_coord = mod.Matrix(data_obj.get('local_coord', None))
            obj = mod.BaseObject.search_obj(data_obj['name'], mod.context_obj)

            # Todo: other args -> matrix
            # Todo: set attribute
            # M_Input = (ML * LC)^(-1) * M_Output * MR^(-1) * LC
            matrix_left = (mod.Matrix(data_obj.get('mat_left', None))
                           * local_coord).invert()
            matrix_right = (mod.Matrix(data_obj.get('mat_right', None)).invert()
                            * local_coord)

            for i in mod.get_frames(range):
                # mod.set_frame(i)
                # Todo: Time Complexity
                obj.set_matrix(
                    matrix_left
                    * mod.Matrix(numlist_convert(
                        output.get_transform(id_obj, i),
                        data_obj.get('indexes', None)
                    )) * matrix_right, i
                )


'''
def read_prop():
    global data
    data = RigProp(path_prop)
    data.list_rigs()
    if PLATFORM == 'c4d':
        data.set_rig('varcade')
    else:
        data.set_rig('varcade-bl')
'''

if __name__ == '__main__':
    if COMMAND == 'get_action':
        get_action()
    elif COMMAND == 'set_action':
        set_action()
    mod.add_event()
