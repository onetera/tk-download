# :coding: utf-8

from ftputil import ftputil, ftp_error

# print(ftputil)
# print(ftp_error)

class ftpHost(ftputil.FTPHost):
    def __init__(self,ftp_host, ftp_user, ftp_pass):
        ftputil.FTPHost.__init__(self,ftp_host,ftp_user,ftp_pass)

        try:
            # 연결 상태 확인
            self.listdir("/")
            print("westworld ftp server connected!!!")
        except ftp_error.FTPOSError:
            print("westworld ftp server connection failed!!!")
            
        self._set_root()
        self._cehck_log_folder()

    def _cehck_log_folder(self):
        self.__log_path = self._root + "log"
        if not self.path.exists(self.__log_path):
            self.makedirs(self.__log_path)

    def _get_log_path(self):
        return self.__log_path
    
    def _list_cur_dir(self):
        return self.curdir
    
    def _set_root(self):
        self._root = self.getcwd()

    def _down(self, src, dest):
        self.download(src, dest)
        print(src, " ===>>> COPY ===>>> ", dest)


