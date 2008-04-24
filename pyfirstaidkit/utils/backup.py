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
import shutil
import hashlib
import weakref

class BackupException(Exception):
    pass

class BackupStoreInterface(object):
    class Backup:
        def __init__(self, id):
            raise NotImplemented()

        def backupPath(self, path, name = None):
            raise NotImplemented()
        def backupValue(self, value, name):
            raise NotImplemented()

        def restoreName(self, name, path = None):
            raise NotImplemented()
        def restorePath(self, path, name = None):
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

class FileBackupStore(BackupStoreInterface):
    _singleton = None

    class Backup(BackupStoreInterface.Backup):
        def __init__(self, id, path):
            self._id = id
            self._path = path
            self._data = {} # name -> (stored as, origin)
            self._origin = {} # origin -> name
            os.makedirs(self._path)

        def backupPath(self, path, name = None):
            if name is None:
                name = path

            if self._origin.has_key(path):
                raise BackupException("Path %s already in the backup store %s!" % (path,self._id))
            if self._data.has_key(name):
                raise BackupException("Named backup %s already in the backup store %s!" % (name,self._id))

            stored = hashlib.sha224(name).hexdigest()

            if os.path.isdir(path):
                shutil.copytree(path, os.path.join(self._path, stored), symlinks = True)
            else:
                shutil.copy2(path, os.path.join(self._path, stored))

            self._origin[path] = name
            self._data[name] = (stored, path)
            return True
        
        def restoreName(self, name, path = None):
            stored, origin = self._data[name]
            assert self._origin[name]==origin

            if path is None:
                path = origin

            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)

            stored = os.join(self._path, stored)
            
            if os.path.isdir(stored):
                shutil.copytree(stored, path, symlinks = True)
            else:
                shutil.copy2(stored, path)
            return True

            
        def restorePath(self, path, name = None):
            assert self._data[self._origin[path]][1]==path

            if name is None:
                name = self._origin[path]

            return self.restoreName(name, path)

        def delete(self, name):
            stored, origin = self._data[name]
            stored = os.join(self._path, stored)

            if os.path.isdir(stored):
                shutil.rmtree(stored)
            else:
                os.unlink(stored)
            return True

        def cleanup(self):
            for name,(stored,origin) in self._data.iteritems():
                self.delete(name)
            os.rmdir(self._path)

    def __init__(self, path):
        if self.__class__._singleton:
            raise BackupException("BackupStore with %s type can have only one instance" % (self.__name__,))

        assert self.__class__._singleton==None

        self._path = path
        self._backups = {}
        os.makedirs(self._path)
        self.__class__._singleton = weakref.proxy(self)
        print "Backup system initialized"

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
        if self.__class__._singleton is None:
            return

        for id,backup in self._backups.iteritems():
            backup.cleanup()
        os.rmdir(self._path)
        print "Backup closed"

    @classmethod
    def get(cls, path):
        if cls._singleton:
            return cls._singleton
        else:
            return cls(path)

