# :coding: utf-8

# import host as host
import os
import time
import datetime


class Download:
    def __init__(self, dest, _item, _ftp_host):
        self._dest_path = dest
        self._down_item = _item
        self._ftp_host = _ftp_host
        self._download_start()
        self.__return()

    def __return(self):
        return self

    def _download_start(self):
        self._ftp_host._down(self._down_item[0],self._dest_path)
        self._down_item[-1] = True
        return self._down_item
    
    @property
    def _result(self):
        return self._down_item
        