# File name: backup.py
# Date:      2008/03/14
# Author:    Martin Sivak <msivak at redhet dot com>
#
# Copyright (C) Red Hat 2008
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# in a file called COPYING along with this program; if not, write to
# the Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA
# 02139, USA.
from errors import NotImplemented
import os

class BackupException(Exception):
    pass

class BackupStoreIterface(object):
    class Backup:
        def __init__(self, id):
            raise NotImplemented()

        def backupPath(self, path, name = None):
            raise NotImplemented()
        def backupValue(self, value, name):
            raise NotImplemented()

        def restorePath(self, name, path = None):
            raise NotImplemented()
        def restoreValue(self, name):
            raise NotImplemented()

        def delete(self, name):
            raise NotImplemented()
        def cleanup(self):
            raise NotImplemented()

    def __init__(self):
        raise NotImplemented()

    def getBackup(self, id):
        raise NotImplemented()

    def closeBackup(self, id):
        raise NotImplemented()

    def __del__(self):
        raise NotImplemented()

class FileBackupStore(BackupStoreIterface):
    _singleton = None

    class Backup(BackupStoreIterface.Backup):
        def __init__(self, id, path):
            self._id = id
            self._path = path

    def __init__(self, path):
        if self.__class__._singleton:
            raise BackupException("BackupStore with %s type can have only one instance" % (self.__name__,))

        assert self.__class__._singleton==None

        self.__class__._singleton = self
        self._path = path
        self._backups = {}

    def getBackup(self, id):
        if not self._backups.has_key(id):
            self._backups[id] = self.Backup(id, self._path+"/"+id+"/")
        return self._backups[id]

    def closeBackup(self, id):
        if not self._backups.has_key(id):
            raise BackupException("Backup with id %s does not exist" % (id,))
        self._backups[id].cleanup()
        del self._backups[id]

    def __del__(self):
        for id,backup in self._backups[id].iteritems():
            backup.cleanup()

    @classmethod
    def get(cls, path):
        if cls._singleton:
            return cls._singleton
        else:
            return cls(path)

