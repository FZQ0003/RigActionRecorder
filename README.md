# RigActionRecorder - 跨平台MC人模记录脚本
Blender &lt;bpy> JSON &lt;c4dpy> Cinema 4D

Last Update: 2020-08-11

Hint: The document is written in Chinese and you may need a translator.

**Do NOT edit files if you DON'T know what it is!!!**

---
### Information - 说明

该项目的定位是一套“跨平台”脚本。通过一个媒介，将不同平台不同种类的MC人模的数据进行处理，以此做到互通。

想法挺好，但是这项工程却拖了半年，期间又重新设计了两次。本来希望能做到设置自定义变换，但是很复杂，只能用“矩阵”这种看似简洁实则需要数学基础的形式了。

考虑到人模功能复杂性，以及对分离控制的处理等问题，本项目仅支持给主要部分k帧。

> *~~说白了就是懒~~*

未来可能会简化自定义，并添加GUI，等等。

> *~~论为啥我要用汉语？因为我英语不行……~~*

---
### Usage - 用法

* 下载zip包并解压。

    > 下载方式：Clone or download -> Download ZIP。

* 打开C4D或Blender，导入人模并k帧。

    > 目前仅支持[Varcade](https://www.bilibili.com/video/av83892718 "Voxel-Arcade团队在动画里使用的人模，由游客Yuke制作")人模，如有其他需求可修改prop.json。\
      Cinema 4D：点上面的链接\
      Blender人模下载：[下载地址](https://fqilin.lanzous.com/b015decja "Varcade_BL")

* 准备完成后，选中人模整体。

    * C4D中：打开“脚本 -> 脚本管理器”。（快捷键Shift+F11）

    * Blender中：转到“Script”界面。

* 在新窗口打开文件“main.py”。

* 根据实际情况，将“SCRIPT_DIR”和“COMMAND”分别改为文件所在目录和指令 [get_action|set_action]

* 最后会在脚本目录下生成“output.json”文件，或者是自动给人模k帧。

    > 目前能复制的控制器非常少，因为我需要记录所有的控制器名称以及局部坐标系矩阵，然后写到prop.json……\
      如果你希望记录自己的人模，可以照着prop.json和schema_prop.json自己写一个。\
      可以百度“json schema”了解schema的用法。

---
### Others - 其他

终于完成了……接下来是完善了……

---
### [Something has changed... ?](https://www.bilibili.com/video/av49330021/?t=2m31s "ああ 君は変った")