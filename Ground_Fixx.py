import os
import shutil
from ctypes import WinDLL, WinError, get_last_error
from stat import \
    FILE_ATTRIBUTE_ARCHIVE as A, FILE_ATTRIBUTE_SYSTEM as S, \
    FILE_ATTRIBUTE_HIDDEN as H, FILE_ATTRIBUTE_READONLY as R, \
    FILE_ATTRIBUTE_NOT_CONTENT_INDEXED as I

def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        try:
            if entry.is_dir(follow_symlinks=False):
                yield from scantree(entry.path)
            else:
                yield entry
        except:
            print('Access Error '+ entry.path)
            pass

def myattrib(kernel32, entry, update=False, a=None, s=None, h=None, r=None, i=None):

    # get the file attributes as an integer.
    if not update: # faster
        attrs = entry.stat(follow_symlinks=False).st_file_attributes
    else: # slower but reflects changes
        # notice that this will raise a WinError Access denied on some entries,
        # for example C:\System Volume Information\
        attrs = os.stat(entry.path, follow_symlinks=False).st_file_attributes

    # construct the new attributes
    newattrs = attrs
    def set(attr, value):
        nonlocal newattrs
        # use '{0:032b}'.format(number) to understand what this does.
        if value is True: newattrs = newattrs | attr
        elif value is False: newattrs = newattrs & ~attr
    set(A, a)
    set(S, s)
    set(H, h)
    set(R, r)
    set(I, i if i is None else not i)
    # optional add more attributes here, see
    # https://docs.python.org/3/library/stat.html#stat.FILE_ATTRIBUTE_ARCHIVE

    # write the new attributes if they changed
    if newattrs != attrs:
        if not kernel32.SetFileAttributesW(entry.path, newattrs):
            raise WinError(get_last_error())

    # return an info tuple
    return (
        bool(newattrs & A),
        bool(newattrs & S),
        bool(newattrs & H),
        bool(newattrs & R),
        not bool(newattrs & I)
    )

if __name__ == '__main__':

    print ('\n\tGround_fixx by RathHunt :V')
    print ('\t'+'*'*26+'\n')

    modify= input('Fix? (1 for fix / 2 for just list)\n')
    print ('Working...')
    kernel32 = WinDLL('kernel32', use_last_error=True)

    path = '.'

    for entry in scantree(path):
        if entry.is_file() and entry.name.startswith('g') and entry.name.endswith('.exe'):
            a,s,h,r,i = myattrib(kernel32, entry)
            #print(entry.path, a,s,h,r,i)
            if s==1 and h==1:
                print(entry.path)
                if(modify == '1'):
                    print('\t' + entry.path + ' -> ' + entry.path[:-len(entry.name)] + entry.name [1:])
                    myattrib(kernel32, entry, a=None, s=False, h=False, r=None, i=None)
                    shutil.move(entry.path, entry.path[:-len(entry.name)] + entry.name [1:])

    input('Completed, press any key to exit')