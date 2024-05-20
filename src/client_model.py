from pathlib import Path
import hashlib
from typing import Optional

class NodeFS:

    def __init__(self, root_path):
        self.root_path:Path = Path(root_path)


    def get_directory_info(self, path:str='/') -> dict[str,dict]:
        relative_local_path:Path = self._localise_path(Path(path))

        if not relative_local_path.is_dir():
            raise ValueError(f"Supplied path is not a directory. {path=}")
            
        return_dict = {
            "path": path,
            "contents": []
        }
        for fs_object_path in relative_local_path.iterdir():
            contents_list = return_dict["contents"]
            contents_list.append(fs_object_to_dict(fs_object_path)) 

        return return_dict


    def _localise_path(self, path:Path):
        parts = path.parts
        if len(parts) < 2:
            relative_local_path = self.root_path
        elif parts[0] == '/':
            relative_local_path = Path(self.root_path, *parts[1:])
        else:
            raise ValueError(f"Relative paths are not accepted. Got path {path}")

        return relative_local_path


def fs_object_to_dict(path:Path):
    return_dict = {
        "name": path.name,
        "mtime": path.lstat().st_mtime,  
    }
    if path.is_dir():
        return_dict["type"] = 'directory'
        return_dict["n_items"] = str(len(list(path.iterdir())))
        return_dict["sha256_hash"] = ""
    else:
        return_dict["type"] = 'file'
        return_dict["n_items"] = ""
        return_dict["sha256_hash"] = get_sha256_hash(path)
    return return_dict


def get_sha256_hash(path:Path):
        BUF_SIZE = 65536
        sha256 = hashlib.sha256()

        with path.open('rb') as fp:
            while True:
                data = fp.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data) 

        return sha256.hexdigest()