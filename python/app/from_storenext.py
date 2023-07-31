# :coding: utf-8

import os
import platform
from ftplib import FTP

'''
vender_{project_name}을 제시하고,
verder_{project_name}/show/{project}/... 로 사용한다.
'''

class Access(FTP):
    def __init__(self, user_info):
        FTP.__init__(self)
        if platform.system() == "Linux":
            self.connect(host="10.0.20.38") 
        else:
            self.connect("220.127.148.3")
        hosts = user_info[0]
        username = user_info[1]
        password = user_info[2]
        self.set_pasv(False)
        self.login(user=username, passwd=password)


class CopyItem:
    def __init__(self, user_info, copy_item):
        self._ftp = Access(user_info)
        self._copy_item = copy_item

    def Create_dir(self,sub_dirs,current_dir):
        #folder Create
        for sub_dir in sub_dirs:
            current_dir = os.path.join(current_dir, sub_dir)
            if not os.path.exists(current_dir):
                os.makedirs(current_dir)

    def Start(self):
        for i in self._copy_item:
            parent_path = str()
            if "." in i.values()[0].split("/")[:-1][-1]:
                path = i.values()[0].split("/")[:-1]
                path.pop()
                parent_path = "/".join(path)
            else:
                parent_path = "/".join(i.values()[0].split("/")[:-1])
            '''
            /show/wedding/seq/EP01/EP01_S007_0010/plate/org/v001
            /show/wedding/seq/EP01/EP01_S007_0010/plate/org/v002
            /show/wedding/seq/EP01/EP01_S007_0010/plate
            /show/wedding/seq/EP01/EP01_S007_0010/plate
            매 경로마다 ftp경로 변경
            '''
            self._ftp.cwd(parent_path)
            
            #테스트로 다운받을 경로 지정.
            if platform.system() == "Windows":
                local_path = 'C:\\' + parent_path
                relative_path = os.path.relpath(local_path, 'C:\\')
                sub_dirs = relative_path.split(os.path.sep)
                current_dir = 'C:\\'
            elif platform.system() == "Linux":
                local_path = '/storenext3/user/pipeline/minwoo' + parent_path
                relative_path = os.path.relpath(local_path, '/storenext3/user/pipeline/minwoo')
                sub_dirs = relative_path.split(os.path.sep)
                current_dir = '/storenext3/user/pipeline/minwoo'
            elif platform.system() == "Darwin":
                pass

            #다운받을 폴더 생성
            self.Create_dir(sub_dirs,current_dir)
            
            check_is_file = os.path.splitext(i.values()[0])
            if len(check_is_file) != 0:
                file_name = i.values()[0].split('/')[-1]
                # print(os.path.join(local_path,file_name))
                with open(os.path.join(local_path,file_name), 'wb') as save_f:
                    print(save_f)
                    self._ftp.retrbinary("RETR " + file_name, save_f.write, blocksize=262144)
        self._ftp.quit()