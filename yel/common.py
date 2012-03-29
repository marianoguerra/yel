import os
import grp
import pwd

class MetaData(object):
    '''base metadata class'''
    pass

class User(MetaData):
    '''user metadata'''

    def __init__(self, name, id_):
        self.name = name
        self.id = id_

    @classmethod
    def from_path(cls, path):
        return cls.from_stat(os.stat(path))

    @classmethod
    def from_stat(cls, stat):
        uid = stat.st_uid
        name = pwd.getpwuid(uid).pw_name
        return cls(uid, name)

class Group(MetaData):
    '''group metadata'''

    def __init__(self, name, id_):
        self.name = name
        self.id = id_

    @classmethod
    def from_path(cls, path):
        return cls.from_stat(os.stat(path))

    @classmethod
    def from_stat(cls, stat):
        gid = stat.st_gid
        name = grp.getgrgid(gid).gr_name
        return cls(gid, name)

class FileTime(MetaData):
    '''file time metadata'''

    def __init__(self, accessed, modified, ctime):
        self.accessed = accessed
        self.modified = modified
        self.ctime = ctime

    @classmethod
    def from_path(cls, path):
        return cls.from_stat(os.stat(path))

    @classmethod
    def from_stat(cls, stat):
        return cls(stat.st_atime, stat.st_mtime, stat.st_ctime)

class File(MetaData):
    '''file metadata'''

    FILE = "f"
    DIR  = "d"

    def __init__(self, name, path, user, group, time, size, type_=FILE,
            childs=None):
        self.name = name
        self.path = path
        self.user = user
        self.group = group
        self.time = time
        self.size = size
        self.type = type_
        self.childs = None

    @classmethod
    def from_path(cls, path, recursive=False):
        '''build a File object from a path'''
        path = os.path.abspath(path)
        name = os.path.basename(path)
        size = os.path.getsize(path)

        type_ = cls.type_from_path(path)

        stat  = os.stat(path)
        user  = User.from_stat(stat)
        group = Group.from_stat(stat)
        time  = FileTime.from_stat(stat)
        size  = stat.st_size

        return cls(name, path, user, group, time, size, type_)

    @classmethod
    def type_from_path(cls, path):
        '''return file type from file path'''
        if os.path.isdir(path):
            type_ = "d"
        elif os.path.isfile(path):
            type_ = "f"
        else:
            type_ = "?"

        return type_

    @property
    def is_dir(self):
        '''return True if it's a directory'''
        return self.type == "d"

    @property
    def is_file(self):
        '''return True if it's a file'''
        return self.type == "f"
