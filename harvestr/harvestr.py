from pathlib import Path
import click, os, json
from more_itertools import only, one

class Harvestr:
    def __init__(self, target, recycle, source, dry_run = False, verbose = False):
        self.target_path = os.path.abspath(target)
        self.recycle_path = os.path.abspath(recycle) if recycle else None
        self.source_paths = [os.path.abspath(source) for source in source]
        self.dry_run = dry_run
        self.verbose = verbose
        
        # Check if target, recycle and source[] all exist as directories
        if [p for p in (self.source_paths + [self.target_path, self.recycle_path]) if p and not os.path.isdir(p)]:
            raise PathsNotDirectoryException([p for p in (self.source_paths + [self.target_path, self.recycle_path]) if p and not os.path.isdir(p)])

        # Check if target, recycle and source[] all in the same mount
        for source in [p for p in (self.source_paths + [self.recycle_path]) if p]:
            if find_mount_point(source) != find_mount_point(self.target_path):
                raise MountPointException(f'"{source}" is not in the same mount as "{target}" ("{find_mount_point(source)}" != "{find_mount_point(target)}")')
        
    def main(self):
        self.sources = self.get_source()
        self.targets = self.get_target()

        if self.verbose:
            click.echo(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2))
        
        for item in self.sources:
            if [t for t in self.targets if t["path"] == item["path"]] and one([t for t in self.targets if t["path"] == item["path"]])["inode"] != item["inode"]:
                if self.recycle_path:
                    self.move(os.path.join(self.target_path, item["path"]), os.path.join(self.recycle_path, item["path"]))
                else:
                    self.delete(os.path.join(self.target_path, item["path"]))
                
            if not [t for t in self.targets if t["path"] == item["path"]]:
                self.link(item["src"], os.path.join(self.target_path, item["path"]))
        
        for item in self.targets:
            if not [s for s in self.sources if s["path"] == item["path"]]:
                if self.recycle_path:
                    self.move(os.path.join(self.target_path, item["path"]), os.path.join(self.recycle_path, item["path"]))
                else:
                    self.delete(os.path.join(self.target_path, item["path"]))
    
    def delete(self, path):
        click.echo(f'Deleting {path}')
        if not self.dry_run:
            os.remove(path)

    def move(self, src_path, dest_path):
        click.echo(f'Moving {src_path} to {dest_path}')
        if not self.dry_run:
            os.rename(src_path, dest_path)

    def link(self, src_path, dest_path):
        click.echo(f'Linking {src_path} to {dest_path}')
        if not self.dry_run:
            os.link(src_path, dest_path)
        
    def get_source(self):
        return self.get_inodes(*self.source_paths)

    def get_target(self):
        return self.get_inodes(self.target_path)

    def get_inodes(self, *roots):
        result = []
        for root in roots:
            for file in [f for f in Path(root).rglob('*') if f.is_file()]:
                if [r for r in result if r["path"] == str(file.relative_to(root))]:
                    raise OverloadedPathException(f'"{file}" and "{one([r for r in result if r["path"] == str(file.relative_to(root))])["src"]}" overload the path "{str(file.relative_to(root))}"')
                result.append({'path': str(file.relative_to(root)), 'inode': os.stat(file).st_ino, 'src': str(file)})
        return result
    

def find_mount_point(path):
    path = os.path.abspath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)
    return path

class PathsNotDirectoryException(Exception):
    pass

class MountPointException(Exception):
    pass

class OverloadedPathException(Exception):
    pass
