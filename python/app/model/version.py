# :coding: utf-8

from .constant import *

class Version:
    def __init__(self,_shot_id,_sg):
        self._versions = []
        self.get_versions(_shot_id,_sg)

    def get_versions(self,id,_sg):
        filters = [
            ["entity", "is", {"type": "Shot", "id": id}]
        ]

        fields = ["code","sg_status_list",
                  "sg_task","sg_path_to_frames",
                  "sg_path_to_movie",
                  "published_files",
                  "sg_cut_duration"
                  ]
        for i in _sg.find("Version", filters, fields):
            if i['sg_task'] == None:
                self._versions.append(i)
            elif i['sg_task']['name'] not in NOTUSECOMP:
                if i['sg_status_list'] in PUB:
                    self._versions.append(i)

    @property
    def vsersins(self):
        return self._versions