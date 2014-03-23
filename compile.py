# coding: utf-8

from distutils.core import setup
from modulefinder import Module
import py2exe
import glob
import fnmatch
import sys
import os
import shutil
import re


#pygame.font.init() # For some reason


def find_pygame_dlls():
    import pygame
    dlls = []
    pygamedir = os.path.split(pygame.base.__file__)[0]
    for r,d,f in os.walk(pygamedir):
        for files in f:
            if files.lower().endswith(".dll"):
                dlls.append(os.path.join(r, files))
    #l = os.path.join(pygamedir, "libogg-0.dll")
    #if not l in dlls:
    #    dlls.append(l)
    return dlls

PYGAME_DLLS = find_pygame_dlls()

#hack which fixes the pygame mixer and pygame font
origIsSystemDLL = py2exe.build_exe.isSystemDLL # save the orginal before we edit it
def isSystemDLL(pathname):
    # checks if the freetype and ogg dll files are being included

    if (pathname in PYGAME_DLLS) or re.match(".*python\d\d\.dll$", pathname):#("libfreetype-6.dll", "libogg-0.dll", "msvcp71.dll", "dwmapi.dll", "SDL_ttf.dll"):#, "SDL_ttf.dll"):
        return 0
    elif pathname.lower().startswith("c:\\windows"):
        return 1
    return origIsSystemDLL(pathname) # return the orginal function
py2exe.build_exe.isSystemDLL = isSystemDLL # override the default function with this one


class pygame2exe(py2exe.build_exe.py2exe): #This hack make sure that pygame default font is copied: no need to modify code for specifying default font
    def copy_extensions(self, extensions):
        import pygame
        #Get pygame default font
        pygamedir = os.path.split(pygame.base.__file__)[0]
        pygame_default_font = os.path.join(pygamedir, pygame.font.get_default_font())

        #Add font to list of extension to be copied
        extensions.append(Module("pygame.font", pygame_default_font))

        # Copy all pygame dll's
        for dll in PYGAME_DLLS:
            try:
                m = Module("pygame", dll)
                m.__pydfile__ = ".".join(dll.split(".")[:-1]) + ".pyd"
                #extensions.append(m)
            except Exception:
                print "Warning, couldn't load", dll

        py2exe.build_exe.py2exe.copy_extensions(self, extensions)

class Builder(object):
    def __init__(self):
        # To find more info visit:
        # http://www.py2exe.org/index.cgi/ListOfOptions
        # http://docs.python.org/2/distutils/apiref.html

        # Project
        self.project_name = ""
        self.project_description = ""
        self.project_url = ""
        self.project_version = ""
        self.license = ""
        self.project_long_description = ""

        # Auhor of program
        self.author_name = ""
        self.author_email = ""
        self.copyright = ""

        # Destination dir
        self.dist_dir = "dist"    # Directory in which to build the final files
        self.extra_datas = []     # Extra files/dirs copied to dist_dir

        # Includes & excludes
        self.extra_modules = []   # List of module names to include
        self.exclude_modules = [] # List of module names to exclude
        self.ignore_modules = []  # List of modules to ignore if they are not found
        self.extra_packages = []  # list of packages to include with subpackages
        self.exclude_dll = []     # List of dlls to exclude
        self.typelibs = []        # List of gen_py generated typelibs to include
        
        # Archive
        self.bundle_files = 1     # Bundle dlls in the zipfile or the exe. { 3: don't bundle, 2: bundle everything but the Python interpreter, 1: bundle everything.
        self.zipfile_name = None  # Name of shared zipfile to generate. If zipfile is set to None, the files will be bundled within the executable.
        self.compressed = True    # Create a compressed zipfile
        self.skip_archive = False # Do not place Python bytecode files in an archive, put them directly in the file system
        
        # Other
        self.optimize = 0         # Code optimization level [0, 1, 2]
        self.unbuffered = False   # Unbuffered stdout
        self.xref = False         # Show a module cross reference
        self.ascii = False        # Do not automatically include encodings and codecs
        self.custom_boot = None   # Python file that will be run when setting up the runtime environment
        self.icon_file = None     # Icon file
        
        # Scripts
        self.console = [] # See add_console
        self.windows = [] # See add_windows
        self.service = [] # See add_service
        self.com_server = [] # See add_com_server
        self.ctypes_com_server = [] # See add_ctypes_com_server
        
        self.to_rename = [] # See rename
        
        
        self.setup()

    def setup(self): # Setup your own parameters
        pass
    
    def prebuild(self): # Customize build process
        pass
    
    def postbuild(self): # Customize build process
        raw_input("Press any key to quit")
        
    def add_console(self, script, rename):
        r = { 'script': script, 'copyright': self.copyright, }
        if rename:
            self.rename(script.rsplit(".", 1)[0] + ".exe", rename) 
        self.console.append(r)
    
    def add_windows(self, script, rename = None, *icons):
        r = { 'script': script, 'copyright': self.copyright, }
        i = []
        for icon in icons:
            i.append((0, icon))
        if len(i):
            r['icon_resources'] = i
        if rename:
            self.rename(script.rsplit(".", 1)[0] + ".exe", rename)
        self.windows.append(r)

    
    def add_service(self, s): # TO DO
        self.service.append(s)
    
    def add_com_server(self, s): # TO DO
        self.com_server.append(s)
    
    def add_ctypes_com_server(self, s): # TO DO
        self.ctypes_com_server.append(s)
    
    def rename(self, name, to):
        self.to_rename.append((name, to))
    
    def add_popular_excludes(self):
        self.exclude_modules += ['Tkinter', 'numpy', '_ssl', 'pyreadline', 'difflib', 'doctest', 'optparse', 'unittest']
        self.exclude_dll += ['w9xpopen.exe', 'tk85.dll', 'tcl85.dll']
    
    def add_pygame_includes(self):
        self.extra_modules += ["pygame", "pygame._view"]

    ## Code from DistUtils tutorial at http://wiki.python.org/moin/Distutils/Tutorial
    ## Originally borrowed from wxPython's setup and config files
    def _opj(self, *args):
        path = os.path.join(*args)
        return os.path.normpath(path)

    def _find_data_files(self, srcdir, *wildcards, **kw):
        # get a list of all files under the srcdir matching wildcards,
        # returned in a format to be used for install_data
        def walk_helper(arg, dirname, files):
            if '.svn' in dirname:
                return
            names = []
            lst, wildcards = arg
            for wc in wildcards:
                wc_name = self._opj(dirname, wc)
                for f in files:
                    filename = self._opj(dirname, f)

                    if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                        names.append(filename)
            if names:
                lst.append( (dirname, names ) )

        file_list = []
        recursive = kw.get('recursive', True)
        if recursive:
            os.path.walk(srcdir, walk_helper, (file_list, wildcards))
        else:
            walk_helper((file_list, wildcards),
                        srcdir,
                        [os.path.basename(f) for f in glob.glob(self._opj(srcdir, '*'))])
        return file_list
    
    def build_config(self):
        options = {
                    'unbuffered' : self.unbuffered,
                    'optimize' : self.optimize,
                    'includes' : self.extra_modules,
                    'packages' : self.extra_packages,
                    'ignores' : self.ignore_modules,
                    'excludes' : self.exclude_modules,
                    'dll_excludes' : self.exclude_dll,
                    'dist_dir' : self.dist_dir,
                    'typelibs' : self.typelibs,
                    'compressed' : self.compressed,
                    'xref' : self.xref,
                    'bundle_files' : self.bundle_files,
                    'skip_archive' : self.skip_archive,
                    }
        args = {
                'cmdclass' : {'py2exe': pygame2exe},
                'version' : self.project_version,
                'description' : self.project_description,
                'long_description' : self.project_long_description,
                'name' : self.project_name,
                'url' : self.project_url,
                'author' : self.author_name,
                'author_email' : self.author_email,
                'license' : self.license,
                'zipfile' : self.zipfile_name,
                'data_files' : self.extra_datas_,
                
                'options' : {'py2exe' : options},
                
                'console' : self.console,
                'windows' : self.windows,
                'service' : self.service,
                'com_server' : self.com_server,
                'ctypes_com_server' : self.ctypes_com_server,
                }
        return args

    def run(self):
        if "py2exe" not in sys.argv: # Make sure py2exe will run
            sys.argv.append("py2exe")
            
        if os.path.isdir(self.dist_dir): #Erase previous destination dir
            print "Removing", os.path.abspath(self.dist_dir)
            shutil.rmtree(self.dist_dir)
        
        self.prebuild()
        
        #List all data files to add
        self.extra_datas_ = []
        for data in self.extra_datas:
            if os.path.isdir(data):
                self.extra_datas_.extend(self._find_data_files(data, '*'))
            else:
                self.extra_datas_.append(('.', [data]))
        #self.extra_datas_.append(('.', glob.glob('*.dll')))
        #self.extra_datas_.append(('.', PYGAME_DLLS))
        #self.extra_modules += [ "pygame", "pygame.font", "pygame._view", "pygame.mixer"]

        setup(**self.build_config()) # Build config and run setup

        if os.path.isdir('build'): #Clean up build dir
            print "Removing", os.path.abspath("build")
            shutil.rmtree('build')
        
        for f, t in self.to_rename:
            print "Renaming", f, "to", t
            os.rename("%s/%s" % (self.dist_dir, f), "%s/%s" % (self.dist_dir, t))
        
        self.postbuild()
            
        print "Build finished successfully!"
            
        

if __name__ == '__main__':
    Builder().run()
    
