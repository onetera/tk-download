# :coding: utf-8

import re
from .task import *
from .version import *
from downitempath import *

'''
Comp Task 작업에 필요한 데이터를 분리하고 관리
'''
class CompItemRegister:
    def __init__(self, selectItem, _sg):
        print("CompItemRegister")
        self._sg = _sg
        self._shot_id = selectItem['entity']['entity']['id']
        self.frame_range = self.get_frame()
        self._all_versions = Version(self._shot_id,self._sg).vsersins
        self._org = []
        self._editor = []
        self._src = []
        self._versions = []
        self._download_register_items = []
        self.parser(self._all_versions)
        self.code_name = selectItem['entity']['entity']['name']
        self.register_item(self._org)
        self.register_item(self._editor)
        self.register_item(self._src)

        # self.register_item(self._versions,"version")
        
    def parser(self, all_versions):
        for ver in all_versions:
            if ver['sg_task'] == None and 'org' in ver['code']:
                self._org.append(ver)
            elif ver['sg_task'] == None and 'editor' in ver['code']:
                self._editor.append(ver)
            elif ver['sg_task'] == None and 'src' in ver['code']:
                self._src.append(ver)
            else:
                self._versions.append(ver)

    def get_frame(self):
        fields = ["sg_cut_in", "sg_cut_out"]
        filters = [["id", "is", self._shot_id]]
        result = self._sg.find_one("Shot", filters, fields)
        return (result['sg_cut_in'],result['sg_cut_out'])
    
    def get_cut_count(self,items):
        cut_count = {}
        for i in items:
            temp = self.get_version(i['code'])
            cut_count[temp] = i['sg_cut_duration']
        return cut_count
        
    def get_version(self,str):
        pattern = r"v\d{3}"
        match = re.search(pattern, str)
        if match:
            part_to_extract = match.group()
        return part_to_extract
        
    def register_item(self,items,type=None):
        #TODO : 각 테스크 별 추가해야함.
        for item in items:
            if type:
                if item['sg_task']['name'] == "matte":
                    pass
                elif item['sg_task']['name'] == "lgt":
                    pass
                elif item['sg_task']['name'] == "mm":
                    pass
                elif item['sg_task']['name'] == "fx":
                    pass
                elif item['sg_task']['name'] == "gen":
                    pass
            else:
                item_name = item['sg_path_to_frames'].split("/")[-1]
                # item_name = item['sg_path_to_movie'].split("/")[-1]
                cut_count = str()
                if "org" in item_name:
                    cut_count = self.get_cut_count(self._org)
                elif "editor" in item_name:
                    cut_count = self.get_cut_count(self._editor)
                else:
                    cut_count = self.get_cut_count(self._src)
                
                # mp4 = item['sg_path_to_movie'].replace('.mov','.mp4')
                # self._download_register_items.append(DownItemPath(item['code'],mp4).item)    
                # self._download_register_items.append(DownItemPath(item['code'],item['sg_path_to_movie']).item)
                version = self.get_version(item['code'])
                if "editor" not in item_name:
                    for frame_number in range(1, cut_count[version] + 1):
                        new_file = item['sg_path_to_frames'].replace('%04d',str(frame_number + 1000))
                        self._download_register_items.append(DownItemPath(item['code'],new_file).item)

    @property
    def get_download_items(self):
        return self._download_register_items
