# :coding: utf-8

class DownItemPath:
    def __init__(self, code, sg_path_to_frames):
        _code = code
        _path = sg_path_to_frames
        self._item = dict()
        self._item[_code] = _path

    @property
    def item(self):
        return self._item