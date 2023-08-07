# :coding: utf-8

import os
import platform
import time
import datetime
from ftplib import FTP, error_temp , error_perm
from io import StringIO
from io import BytesIO
from datetime import datetime
from sgtk.platform.qt import QtCore, QtGui


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
        self.set_pasv(True)
        self.login(user=username, passwd=password)
        self._log_path = self.pwd()

    @property
    def log_path(self):
        return self._log_path

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

    def create_log_file(self,text,filename,bool=True):
        with BytesIO(text.encode("utf-8")) as ftp_log:     
            if bool:
                self._ftp.storlines('APPE ' + filename, ftp_log)
            else:
                self._ftp.storlines('STOR ' + filename, ftp_log)

    def log(self,data):
        filename = datetime.today().strftime("%Y%m%d") + ".log"
        self._ftp.cwd("/log")
        file_list = []
        self._ftp.dir("/log", file_list.append)
        #로그파일이 하나도 없을 경우 
        log_text = "\n".join(data)
        if len(file_list) != 0:
            for file in file_list:
                if filename == file.split(" ")[-1]:
                    existing_log = self._ftp.retrlines('RETR ' + filename)
                    new_log_text = existing_log + "\n" + "\n".join(data)
                    self.create_log_file(new_log_text, filename)
                else:
                    self.create_log_file(log_text,filename)
        else:
            self.create_log_file(log_text,filename,False)
        print("Create Log file")
        self._ftp.cwd("/")

    def Start(self, func, path, ui):
        filename = datetime.today().strftime("%Y%m%d") + ".log"

        log_data = list()
        log_data.append("=================================================")
        log_data.append(datetime.today().strftime("%Y/%m/%d %H:%M:%S\n"))
        
        for index,i in enumerate(self._copy_item):
            parent_path = str()
            if "." in i.values()[0].split("/")[:-1][-1]:
                path = i.values()[0].split("/")[:-1]
                path.pop()
                parent_path = "/".join(path)
            else:
                parent_path = "/".join(i.values()[0].split("/")[:-1])

            self._ftp.cwd(parent_path)
            
            local_path = path + parent_path
            relative_path = os.path.relpath(local_path, path)
            sub_dirs = relative_path.split(os.path.sep)
            current_dir = path

            #다운받을 폴더 생성
            self.Create_dir(sub_dirs,current_dir)
        
            check_is_file = os.path.splitext(i.values()[0])
            if len(check_is_file) != 0:
                file_name = i.values()[0].split('/')[-1]
                try:
                    with open(os.path.join(local_path,file_name), 'wb') as save_f:
                        log_data.append(i.values()[0])
                        mapped_value = round(index*(100.0 / len(self._copy_item)))
                        ui.progress.setValue(mapped_value)
                        self._ftp.retrbinary("RETR " + file_name, save_f.write, blocksize=262144)

                except error_temp as e:
                    print(e)
                except error_perm as r:
                    print("=================================================")
                    print(r)
                    print("=================================================")

        log_data.append("=================================================")
        
        self.log(log_data)

        self._ftp.quit()
        return 0
