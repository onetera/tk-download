# :coding: utf-8

from .constant import *

class Version:
    def __init__(self,_shot_id,_sg):
        self._versions = []
        self.get_versions(_shot_id,_sg)

    def get_versions(self,id,_sg):
        version_types = ['org', 'src', 'editor']

        for version_type in version_types:
            last_version = _sg.find_one(
                "Version",
                filters=[["entity", "is", {"type": "Shot", "id": id}],
                    [ 'sg_version_type', 'is', version_type ]
                    ],
                
                fields=["code","sg_status_list",
                        "sg_task","sg_path_to_frames",
                        "sg_path_to_movie",
                        "published_files",
                        "sg_cut_duration",
                        ],
                order=[
                        {'field_name':'id','direction':'desc'}
                    ]
            )
            if last_version is not None:
                self._versions.append(last_version)        

        # filters = [
        #     ["entity", "is", {"type": "Shot", "id": id}]
        # ]

        # fields = ["code","sg_status_list",
        #           "sg_task","sg_path_to_frames",
        #           "sg_path_to_movie",
        #           "published_files",
        #           "sg_cut_duration",
        #           "sg_version_type"
        #           ]
        # for i in _sg.find("Version", filters, fields):
        #     if i['sg_task'] == None:
        #         self._versions.append(i)
        #     elif i['sg_task']['name'] not in NOTUSECOMP:
        #         if i['sg_status_list'] in PUB:
        #             self._versions.append(i)

    @property
    def vsersins(self):
        return self._versions