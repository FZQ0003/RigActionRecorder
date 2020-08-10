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


class Output(DataJson):

    def __init__(self, path=None):
        super(Output, self).__init__(path)
        if path is None:
            self._data['data_version'] = 0.1
            self._data['frame_range'] = mod.get_frames(list)
            self._data['data'] = []
            self._data['fps'] = mod.get_fps()
        else:
            mod.init_settings(
                self._data['frame_range'][0],
                self._data['frame_range'][1],
                self._data['fps']
            )

    def get_data(self):
        return self._data.get('data', [])

    def append_data(self, input_data):
        """

        :type input_data: dict
        :param input_data:
        :return:
        """
        self._data['data'].append(input_data.copy())

    def get_transform(self, id_obj, frame):
        """

        :type frame: int
        :param frame:
        :type id_obj: str
        :param id_obj:
        :return:
        :rtype: mod.Matrix
        """
        for obj in self.get_data():
            if obj['id'] == id_obj:
                return mod.Matrix(obj.get('%04d' % frame, None))
        return mod.Matrix()


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

    for id_obj in data.list_objects():
        data_obj = data.get_object(id_obj)
        # Todo: other args -> matrix
        if data_obj.get('readable', True):
            transform = mod.Matrix(data_obj.get('transform', None))
            obj = mod.BaseObject.search_obj(data_obj['name'], mod.context_obj)

            output_data = {'id': id_obj}
            for i in mod.get_frames(range):
                mod.set_frame(i)
                output_data['%04d' % i] = (
                    transform
                    * obj.get_matrix(i)
                    * transform.invert()
                ).convert_to_list()
            output.append_data(output_data)

    output.save_text(path_output)


def set_action():
    output = Output(path_output)

    for id_obj in data.list_objects():
        data_obj = data.get_object(id_obj)
        # Todo: other args -> matrix
        if data_obj.get('readable', True):
            transform = mod.Matrix(data_obj.get('transform', None))
            obj = mod.BaseObject.search_obj(data_obj['name'], mod.context_obj)

            for i in mod.get_frames(range):
                # mod.set_frame(i)
                # Todo: Time Complexity
                obj.set_matrix(
                    transform.invert()
                    * output.get_transform(id_obj, i)
                    * transform, i
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
