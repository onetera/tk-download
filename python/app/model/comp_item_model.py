# :coding: utf-8

import re
# from path_model import *

PUB = [
    't-pub',
    'fin',
    'pub',
    's_ok'
]

MMPUBTYPE = [
    'Camera USD',
    'Guide USD',
    'Maya Scene',
    'Nuke Script',
    'undistort_jpg',
    'Component USD',
    'Alembic Cache'
]

NOTUSECOMP = [
    "motion",
    "ani",
    "layout"
    "comp"
]

def recursive_unique_files(directory, temp):
    unique_files = set()
    for entry in os.listdir(directory):
        entry_path = os.path.join(directory, entry)

        if os.path.isdir(entry_path):
            recursive_unique_files(entry_path,temp)

        elif os.path.isfile(entry_path):
            filename, ext = os.path.splitext(entry)
            if ext in entry :
                # entry = re.sub(r'(\d+)', r'%04d', entry)
                temp.append(os.path.join(entry_path,entry))
                # break

            if filename not in unique_files:
                unique_files.add(filename)
    # print(temp)
    return temp


class Task:
    def __init__(self, _shot_id, _sg):
        self.get_task(_shot_id,_sg)

    def get_task(self,id,_sg):
        print(id)
        filters = [
            ["entity", "is", {"type": "Shot", "id": id}]
        ]
        fields = ["id", "content", "sg_status_list"]
        self._tasks = _sg.find("Task", filters, fields)

    @property
    def tasks(self):
        return self._tasks
    

class Version:
    def __init__(self,_shot_id,_sg):
        self._versions = []
        self.get_versions(_shot_id,_sg)

    def get_versions(self,id,_sg):
        filters = [
            ["entity", "is", {"type": "Shot", "id": id}]
        ]

        fields = ["code","sg_status_list","sg_task","sg_path_to_frames","sg_path_to_movie","published_files","sg_cut_duration"]
        for i in _sg.find("Version", filters, fields):
            if i['sg_task'] == None:
                self._versions.append(i)
            elif i['sg_task']['name'] not in NOTUSECOMP:
                if i['sg_status_list'] in PUB:
                    self._versions.append(i)

    @property
    def vsersins(self):
        return self._versions
    
    
class DownItemPath:
    def __init__(self, code, sg_path_to_frames):
        _code = code
        _path = sg_path_to_frames
        self._item = dict()
        self._item[_code] = _path

    @property
    def item(self):
        return self._item
'''
Comp Task 작업에 필요한 데이터를 분리하고 관리
'''
class CompItemRegister:
    def __init__(self, selectItem, _sg):
        self._sg = _sg
        self._shot_id = selectItem['entity']['entity']['id']
        self.frame_range = self.get_frame()
        self._all_versions = Version(self._shot_id,self._sg).vsersins
        self._org = []
        self._editor = []
        self._src = []
        self._versions = []
        self.parser(self._all_versions)
        self.code_name = selectItem['entity']['entity']['name']
        self._download_register_items = []
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
                    print("matte copy")
                    # if len(item['published_files']) != 0: 
                    #     filters = [
                    #     ["id", "is", item['published_files'][0]['id']]
                    #     ]
                    #     fields = ["path_cache"]
                    #     publish_file = self._sg.find_one("PublishedFile",filters, fields)
                    #     self._download_register_items.append(DownItemPath(item['code'],"/show/"+publish_file['path_cache']).item)
                elif item['sg_task']['name'] == "lgt":
                    pass
                    # lgt_item_list = list()
                    # print("lgt copy")
                    # split_str = 'wip/'
                    # split_path = item['sg_path_to_frames'].split(split_str)[0]
                    # version_name = item['code']
                    # # print(split_path)
                    # recursive_unique_files(split_path,lgt_item_list) 
                    # for i in lgt_item_list:
                    #     # print(i)
                    #     self._download_register_items.append(DownItemPath("lgt_item",i).item)
                    # nuke_path = split_path.split('precomp/')[0] + 'nuke/'
                    # nuke_file_list = os.listdir(nuke_path)
                    # filter = ['nk~','nk.autosave']
                    # for nuke in nuke_file_list:
                    #     if not any(f in nuke for f in filter):
                    #         if version_name in nuke:
                    #             # print(os.path.join(nuke_path,nuke))
                    #             self._download_register_items.append(DownItemPath(version_name,os.path.join(nuke_path,nuke)).item)
                elif item['sg_task']['name'] == "mm":
                    pass
                    # print("mm copy")
                    # filters = [["name", "contains",  self.code_name]]
                    # fields = ["code", "name", "path",'task','published_file_type']
                    # published_files = self._sg.find("PublishedFile", filters, fields)
                    # #undistort , nk, mb 3개 추출
                    # for i in published_files:
                    #     if i['task'] != None:
                    #         if i['task']['name'] == 'mm' and i['published_file_type']['name'] in MMPUBTYPE:
                    #             # print(i['path']['local_path'])
                    #             self._download_register_items.append(DownItemPath(i['code'],i['path']['local_path']).item)
                    # self._download_register_items.append(DownItemPath(item['code'],item['sg_path_to_frames']).item)
                    # split_str = 'pub/'
                    # split_path = item['sg_path_to_frames'].split(split_str)[0]
                    # split_path += split_str + "caches/"
                    # cache_in = ['abc','mb','usd']
                    # for cache_path in cache_in:
                    #     path = os.path.join(split_path,cache_path)
                    #     for file in os.listdir(path):
                    #         # print(os.path.join(path,file))
                    #         self._download_register_items.append(DownItemPath(file,os.path.join(path,file)).item)
                elif item['sg_task']['name'] == "fx":
                    pass
                    # print("fx copy")
                elif item['sg_task']['name'] == "gen":
                    pass
                    # prit("gen copy")
            else:
                item_name = item['sg_path_to_movie'].split("/")[-1]
                cut_count = str()
                if "org" in item_name:
                    cut_count = self.get_cut_count(self._org)
                elif "editor" in item_name:
                    cut_count = self.get_cut_count(self._editor)
                else:
                    cut_count = self.get_cut_count(self._src)
                
                mp4 = item['sg_path_to_movie'].replace('.mov','.mp4')
                self._download_register_items.append(DownItemPath(item['code'],mp4).item)    
                self._download_register_items.append(DownItemPath(item['code'],item['sg_path_to_movie']).item)
                version = self.get_version(item['code'])
                if "editor" not in item_name:
                    for frame_number in range(1, cut_count[version] + 1):
                        new_file = item['sg_path_to_frames'].replace('%04d',str(frame_number + 1000))
                        self._download_register_items.append(DownItemPath(item['code'],new_file).item)

    @property
    def get_download_items(self):
        return self._download_register_items
