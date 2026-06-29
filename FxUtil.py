import os


def parse_vfx_filename(filename):
    elements = filename.replace(".", "_").split("_")
    if len(elements) >= 2 and elements[-2].lower().startswith("v"):
        shotname = '_'.join(elements[0:-2])
        version = elements[-2]
        return shotname, version
    return filename, ""


class FxShot():
    def __init__(self,shotname):
        self.shotname = shotname
        self.files = {}
        self.clip = None
        self.status = ""

    def add_file(self,file):
        self.files[file.get_version()] = file
    
    def add_clip(self,clip):
        self.clip = clip
    
    def get_clip(self):
        if self.clip is None:
            return None
        return self.clip
    
    def get_latest_file(self):
        if self.files == {}:
            return None
        return self.files[max(self.files.keys())]
    
    def get_clip_version(self):
        if self.clip is None:
            return ""
        return self.clip.get_version()
    
    def get_all_version(self):
        return self.files.keys()
    
    def get_latest_version(self):
        if self.files == {}:
            return ""
        return max(self.files.keys())
    
    def get_file(self, version):
        if version not in self.files:
            return None
        return self.files[version]
    
    def check_status(self):
        if self.clip is None:
            self.status = "New"
        elif self.files == {}:
            self.status = "No Files"    
        elif self.get_clip_version() != self.get_latest_version():
            self.status = "Need Update"
        else:
            self.status = "OK"
    
    def set_clip_color(self):
        if self.clip is None:
            return
        elif self.get_clip_version() != self.get_latest_version():
            self.clip.clip.SetClipColor("Yellow")
        else:
            self.clip.clip.SetClipColor("Green")

class FxFile():
    def __init__(self,filename,filepath):
        self.filename = filename
        self.filepath = filepath
        self.shotname, self.version = parse_vfx_filename(filename)
        self.set_modified_time()
    
    def set_modified_time(self):
        if not self.filepath:
            self.modified_time = ""
        else:
            self.modified_time = os.path.getmtime(self.filepath)
    
    def get_shotname(self):
        if not self.shotname:
            return None
        return self.shotname
    
    def get_version(self):
        if not self.version:
            return None
        return self.version
    
    def get_filepath(self):
        if not self.filepath:
            return None
        return self.filepath
    
    def get_modified_time(self):
        if not self.modified_time:
            return None
        return self.modified_time

    def import_clip(self,media_pool):
        media = media_pool.ImportMedia([self.filepath])
        return media[0]
        

class FxClip():
    def __init__(self,clip):
        self.clip = clip
        self.name = clip.GetName()
        self.filepath = clip.GetClipProperty("File Path")
        self.shotname, self.version = parse_vfx_filename(self.name)
    
    def get_shotname(self):
        if not self.shotname:
            return None
        return self.shotname
    
    def get_version(self):
        if not self.version:
            return None
        return self.version

    def get_filepath(self):
        return self.filepath

    def replace_clip(self,new_filepath):
        self.clip.ReplaceClip(new_filepath)
    


class FxFolder():
    def __init__(self,path=None ,media_pool=None):
        self.path = path
        self.media_pool = media_pool
        self.fx_shots = {}
        self.update()

    def scan_folder(self,path=None):
        if path is not None:
            self.path = path
        if self.path is None:
            return
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith(".mov") and not file.startswith("."):
                    shotname, version = parse_vfx_filename(file)
                    if shotname not in self.fx_shots:
                        self.fx_shots[shotname] = FxShot(shotname)
                    self.fx_shots[shotname].add_file(FxFile(file, os.path.join(root, file)))
    
    def scan_bin(self,bin):
        if bin is None:
            return
        for clip in bin.GetClipList():
            shotname, version = parse_vfx_filename(clip.GetName())
            if shotname not in self.fx_shots:
                self.fx_shots[shotname] = FxShot(shotname)
            self.fx_shots[shotname].add_clip(FxClip(clip))
        
        subbins = bin.GetSubFolderList()
        if subbins is not None:
            for subbin in subbins:
                self.scan_bin(subbin)

    def scan_media_pool(self,media_pool=None):
        if media_pool is None:
            return
        self.media_pool = media_pool
        bin = media_pool.GetCurrentFolder()
        self.scan_bin(bin)
    
    def check_status(self):
        for shotname, fx_shot in self.fx_shots.items():
            fx_shot.check_status()

    def get_fx_shots(self):
        table = []
        for shotname, fx_shot in self.fx_shots.items():
            table.append([shotname, fx_shot.get_clip_version(),fx_shot.get_latest_version(),fx_shot.status])
        return table

    def get_shot_versions(self, shotname):
        if shotname not in self.fx_shots:
            return None
        return self.fx_shots[shotname].get_all_version()
    
    def get_latest_version(self, shotname):
        if shotname not in self.fx_shots:
            return None
        return self.fx_shots[shotname].get_latest_version()
    
    def get_clip_version(self, shotname):
        return self.fx_shots[shotname].get_clip_version()
    
    def update(self,path=None,media_pool=None):
        self.fx_shots = {}
        self.scan_folder(path)
        self.scan_media_pool(media_pool)
        self.check_status()
    
    def update_clip(self,shotname,version):
        self.fx_shots[shotname].get_clip().replace_clip(self.fx_shots[shotname].get_file(version).get_filepath())
    
    def import_file(self,shotname,version):
        clip = self.fx_shots[shotname].get_file(version).import_clip(self.media_pool)
        return clip

    def update_all(self):
        for shotname, fx_shot in self.fx_shots.items():
            if fx_shot.status == "OK":
                continue
            if fx_shot.status == "Need Update":
                self.update_clip(shotname, fx_shot.get_latest_version())
                fx_shot.get_clip().clip.SetClipColor("Green")
            elif fx_shot.status == "New":
                clip = self.import_file(shotname, fx_shot.get_latest_version())
                clip.SetClipColor("Brown")
    
    def set_clip_colors(self):
        for shotname, fx_shot in self.fx_shots.items():
            fx_shot.set_clip_color()