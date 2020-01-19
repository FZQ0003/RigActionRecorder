# -*- coding: UTF-8 -*-
# Testing: Cinema 4D R19.068


import c4d
import json
import re


fn = 'D:\\C4D\\Python\\example\\prop.json'
output_fn = 'D:\\C4D\\Python\\example\\output_test.json'


def create_id_list():
    """
    内置对应关系, 相比于单向字典效率较高
    """

    global id_list
    id_list = [['location', c4d.ID_BASEOBJECT_REL_POSITION,
                'x', 'h', c4d.VECTOR_X, [0, 2]],
               ['rotation', c4d.ID_BASEOBJECT_REL_ROTATION,
                'y', 'p', c4d.VECTOR_Y, [2, 0]],
               ['scale', c4d.ID_BASEOBJECT_REL_SCALE,
                'z', 'b', c4d.VECTOR_Z, [1, 1]]]
    # H-Z, P-X, B-Y.


def id_search(ele, *ty):
    """
    查内置对应关系(id_list)

    :param ele: 待查内容, 0-2直接指向序号
    :param *ty: 指向其他内容的序号, 默认返回待查序号
    :return: 目标内容(数据/列表)
    """

    global id_list
    flag = 1
    if type(ele) is int and 0 <= ele < 3:
        flag = 0
        lis = id_list[ele]
    else:
        for lis in id_list:
            if ele in lis:
                flag = 0
                break
    if flag:
        return None
    if ty == ():
        return id_list.index(lis)
    tmp_lis = []
    for i in ty:
        if i is None:
            tmp_lis.append(id_list.index(lis))
        else:
            tmp_lis.append(lis[i])
    if len(tmp_lis) > 1:
        return tmp_lis
    else:
        return tmp_lis[0]


def id_conv(id_des, order=1):
    """
    给定类型和方向, 进行id重定向

    :param id_des: 记录类型和方向的元组/列表(DescID/0-2)
    :param order: 重定向方向(1正向&-1逆向), 默认1
    :return: 目标信息(类型, 方向)
    """

    if order < 0:
        pass
    else:
        e_obj = id_search(id_des[0].id, 0, None)
        e_vec = id_search(id_des[1].id, -1, None)
    return [e_obj[0], e_vec[0][e_obj[1]%2], e_obj[1], e_vec[1]]


def prop_judge(prop, *pos_t):
    """
    给定Properties、类型及方向, 判断是否可变换

    :param prop: Properties(Dict)
    :param pos_t: 类型, 方向
    :return: 
    """

    if type(prop) is dict:
        pos = prop.get('pos', None)
    else:
        return -1
    if pos is None:
        return -1
    if type(pos[1]) is not list:
        pos[1] = [pos[1]]
    if pos_t[0] == pos[0] and pos_t[1] in pos[1]:
        return pos[1].index(pos_t[1])
    else:
        return -2


def prop_conv(tar, a1, a2, pos=0):
    """
    给定Properties及若干参数, 进行映射变换

    :param tar: 目标数据(列表/元组/数)
    :param a1: 列表/元组1
    :param a1: 列表/元组2
    :param pos: 
    :return: 变换后数据(列表/数)
    """

    if a1 is None or a2 is None or a1 == a2:
        return tar
    if type(tar) is not list:
        tar = [tar]
    if type(a1[0]) is not list:
        a1 = [a1]
    if type(a2[0]) is not list:
        a2 = [a2]
    lis = []
    for i in tar:
        lis.append(lifunc_cal(ran[pos], val[pos], i))
    if len(lis) > 1:
        return lis
    else:
        return lis[0]


def lifunc_cal(x, y, xn):
    k = 1.0 * (y[0]-y[1]) / (x[0]-x[1])
    b = y[0] - k*x[0]
    return k*xn+b


def search(name, p=op):
    """
    通过给定名称查找相应部件

    :param name: 名称
    :param p: 父级类, 限定在哪个父级内查找
    :return: c4d.BaseObject类型(无匹配为空)
    """

    if p == None:
        return doc.SearchObjectInc(name)
    for i in p.GetChildren():
        if name == i.GetName().decode('utf-8'):
            return i
        else:
            x = search(name, i)
            if x is not None:
                return x
    return None
    #if p == op:
    #    return doc.SearchObjectInc(name)
    #else:
    #    return None


def rig_judge(data, name, ver):
    """
    检查信息

    :param data: 待检测数据块
    :param name: 名称
    :param ver: 版本号
    :return: 布尔值
    """

    a = data['name'] == name
    if type(data['version']) is list:
        b = min(data['version']) < ver < max(data['version'])
    else:
        b = data['version'] == ver
    if type(data['target']) is list:
        c = 0 in data['target']
    else:
        c = data['target'] == 0
    return a and b and c


def rig_record(data):
    return obj_record(data['object'])


def obj_record(base):
    global id_list
    out = {}
    fps = doc[c4d.DOCUMENT_FPS]
    #frame = doc[c4d.DOCUMENT_TIME].GetFrame(doc[c4d.DOCUMENT_FPS])
    for i in base:
        dic = {}
        if type(base[i]) is dict:
            obj_n = base[i].get('name', None)
            if type(obj_n) is list or obj_n is None:
                continue
            obj_p = base[i].get('parent', op)
            if obj_p != op:
                obj_p = search(obj_p)
            pos_ran = base[i].get('range', None)
            pos_val = base[i].get('value', None)
        else:
            obj_n = base[i]
            obj_p = op
            pos_ran = None
            pos_val = None
        obj = search(obj_n, obj_p)
        if obj is None:
            continue
        lis_tmp = None
        for track in obj.GetCTracks():
            id_type = id_conv(track.GetDescriptionID())
            obj_pos = prop_judge(base[i], id_type[-2], id_type[-1])
            if obj_pos == -2:
                continue
            if obj_pos == -1:
                if type(dic.get(id_type[0], None)) is not list:
                    dic[id_type[0]] = [{}, {}, {}]
                dic_tmp = dic[id_type[0]][id_type[1]]
            elif pos_ran is not None and type(pos_ran[0]) is list:
                dic_tmp = dic
                if lis_tmp is None:
                    lis_tmp = [0 for _ in range(len(pos_ran))]
            else:
                dic_tmp = dic
            curve = track.GetCurve()
            for c_i in range(curve.GetKeyCount()):
                key = curve.GetKey(c_i)
                frame = key.GetTime().GetFrame(fps)
                value = prop_conv(key.GetValue(), pos_ran, pos_val, obj_pos)
                if lis_tmp is None:
                    dic_tmp[frame] = round(value, 6)
                else:
                    _lis = dic_tmp.get(frame, None)
                    if _lis is None:
                        lis_tmp[obj_pos] = round(value, 6)
                        dic_tmp[frame] = lis_tmp[:]
                    else:
                        _lis[obj_pos] = round(value, 6)
        if dic != {}:
            out[i] = dic
    txt = json.dumps(out, sort_keys=True, indent=2)

    return txt


def printv(vec):
    for i in range(3):
        print(vec[i])


def main():
    global fn, output_fn
    if op is None:
        c4d.gui.MessageDialog('Please select a rig!', c4d.GEMB_ICONEXCLAMATION)
        return -1
    if op.GetType() == 5101 and op.GetTag(1026275) is not None:
        x = op.GetName()
        # obj = doc.SearchObjectInc(x)
        
        #fn = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_SCENES)
        with open(fn.decode('utf-8'), 'r') as f:
            prop = re.sub(r'/\*.*\*/', '', re.sub(r'//.*', '', f.read()), flags=re.S)
        try:
            prop = json.loads(prop)
        except:
            c4d.gui.MessageDialog('Not a JSON file!', c4d.GEMB_ICONSTOP)
            return 1
        create_id_list()
        rig_name = 'varcade'
        rig_ver = 1.7
        for data in prop['rigs']:
            if rig_judge(data, rig_name, rig_ver):
                with open(output_fn.decode('utf-8'), 'w') as out_f:
                    out_f.write(rig_record(data))
        #vec = obj.GetRelPos()
        #ang = obj.GetRelRot()
        # print(x)
        # printv(vec)
        # printv(ang)
        # c4d.gui.MessageDialog(x)
    else:
        c4d.gui.MessageDialog('Please select the base of the rig!', c4d.GEMB_ICONEXCLAMATION)
        return -1


if __name__=='__main__':
    print('=== START ===')
    main()
    print('=== END ===')
