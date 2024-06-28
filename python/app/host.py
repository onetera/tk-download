# :coding: utf-8

from .ftputil import ftputil, ftp_error
import ftplib

# print(ftputil)
# print(ftp_error)

class ftpHost(ftputil.FTPHost):
    def __init__(self,ftp_host, ftp_user, ftp_pass, ftp_port, retries=False):
        def my_session_factory(*args, **kwargs):
            inst = ftplib.FTP()
            inst.connect(host=ftp_host, port=ftp_port)
            inst.login(user=ftp_user, passwd=ftp_pass)
            return inst
        
        ftputil.FTPHost.__init__(self, ftp_host, ftp_user, ftp_pass, session_factory=my_session_factory)

        try:
            # 연결 상태 확인
            self.listdir("/")
            if retries:
                print("westworld ftp server Reconnected!!!")
            else:
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
        self.download(src, dest, mode='b')
        print(src, " ===>>> COPY ===>>> ", dest)


