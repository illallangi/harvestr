import json
import os
from pathlib import Path

from loguru import logger

from more_itertools import one


class Harvestr:
    def __init__(self, target, recycle, source, dry_run=False):
        self.target_path = os.path.abspath(target)
        self.recycle_path = os.path.abspath(recycle) if recycle else None
        self.source_paths = [os.path.abspath(source) for source in source]
        self.dry_run = dry_run

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

        logger.trace(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2))

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
        logger.success(f'Deleting {path}')
        if not self.dry_run:
            os.remove(path)

    def move(self, src_path, dest_path):
        logger.success(f'Moving {src_path} to {dest_path}')
        if not self.dry_run:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            os.rename(src_path, dest_path)

    def link(self, src_path, dest_path):
        logger.success(f'Linking {src_path} to {dest_path}')
        if not self.dry_run:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            os.link(src_path, dest_path)

    def get_source(self):
        return self.get_inodes(*self.source_paths)

    def get_target(self):
        return self.get_inodes(self.target_path)

    def get_inodes(self, *roots):
        result = []
        for root in roots:
            logger.debug('Getting files in {}', root)
            files = [f for f in Path(root).rglob('*') if f.is_file()]
            for file in files:
                relative = str(file.relative_to(root))
                if [r for r in result if r["path"] == relative]:
                    raise OverloadedPathException(f'"{file}" and "{one([r for r in result if r["path"] == relative])["src"]}" overload the path "{relative}"')
                result.append({'path': relative, 'inode': os.stat(file).st_ino, 'src': str(file)})
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
