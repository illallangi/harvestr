import json
import os
from fnmatch import fnmatch
from os.path import basename, exists
from pathlib import Path

from loguru import logger

from more_itertools import one


class Harvestr:
    def __init__(self, target, recycle, source, exclude=None, include=['*'], dry_run=False):
        self.target_path = os.path.abspath(target)
        self.recycle_path = os.path.abspath(recycle) if recycle else None
        self.source_paths = [os.path.abspath(source) for source in source]
        self.exclude = exclude if exclude else []
        self.include = include if include else ['*']
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
        moved_ok = 0
        moved_err = 0
        deleted_ok = 0
        deleted_err = 0
        linked_ok = 0
        linked_err = 0

        logger.trace(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2))

        for item in self.sources:
            if [t for t in self.targets if t["path"] == item["path"]] and one([t for t in self.targets if t["path"] == item["path"]])["inode"] != item["inode"]:
                if self.recycle_path:
                    if self.move(os.path.join(self.target_path, item["path"]), os.path.join(self.recycle_path, item["path"])):
                        moved_ok += 1
                    else:
                        moved_err += 1
                else:
                    if self.delete(os.path.join(self.target_path, item["path"])):
                        deleted_ok += 1
                    else:
                        deleted_err += 1

            if not [t for t in self.targets if t["path"] == item["path"]]:
                if self.link(item["src"], os.path.join(self.target_path, item["path"])):
                    linked_ok += 1
                else:
                    linked_err += 1

        for item in self.targets:
            if not [s for s in self.sources if s["path"] == item["path"]]:
                if self.recycle_path:
                    if self.move(os.path.join(self.target_path, item["path"]), os.path.join(self.recycle_path, item["path"])):
                        moved_ok += 1
                    else:
                        moved_err += 1
                else:
                    if self.delete(os.path.join(self.target_path, item["path"])):
                        deleted_ok += 1
                    else:
                        deleted_err += 1

        if sum([moved_ok, moved_err, deleted_ok, deleted_err, linked_ok, linked_err]) > 0:
            logger.success("Run completed:")
            if sum([moved_ok, moved_err]) > 0:
                logger.success(f"  Moved {moved_ok} successfully, {moved_err} failed.")
            if sum([deleted_ok, deleted_err]) > 0:
                logger.success(f"  Deleted {deleted_ok} successfully, {deleted_err} failed.")
            if sum([linked_ok, linked_err]) > 0:
                logger.success(f"  Linked {linked_ok} successfully, {linked_err} failed.")

    def delete(self, path):
        logger.debug('Deleting:')
        logger.debug('  {}', path)
        if not exists(path):
            logger.warning('{} disappeared during run', basename(path))
            return False
        if not self.dry_run:
            os.remove(path)
        logger.info('Deleted {}', basename(path))
        return True

    def move(self, src_path, dest_path):
        logger.debug('Moving:')
        logger.debug('  Source {}', src_path)
        logger.debug('  Destination {}', dest_path)
        if not exists(src_path):
            logger.warning('{} disappeared during run', basename(src_path))
            return False
        if exists(dest_path):
            logger.warning('{} already exists', dest_path)
            return False
        if not self.dry_run:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            os.rename(src_path, dest_path)
        logger.info('Moved {}', basename(dest_path))
        return True

    def link(self, src_path, dest_path):
        logger.debug('Linking:')
        logger.debug('  Source {}', src_path)
        logger.debug('  Destination {}', dest_path)
        if not exists(src_path):
            logger.warning('{} disappeared during run', basename(src_path))
            return False
        if not self.dry_run:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            os.link(src_path, dest_path)
        logger.info('Linked {}', basename(dest_path))
        return True

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
                exclude = False
                for e in self.exclude:
                    if fnmatch(str(file), e):
                        exclude = True
                if exclude:
                    logger.debug('{} excluded', basename(str(file)))
                    continue
                include = False
                for e in self.include:
                    if fnmatch(str(file), e):
                        include = True
                if not include:
                    logger.debug('{} not included', basename(str(file)))
                    continue
                relative = str(file.relative_to(root))
                if [r for r in result if r["path"] == relative]:
                    raise OverloadedPathException(f'"{file}" and "{one([r for r in result if r["path"] == relative])["src"]}" overload the path "{relative}"')
                if not exists(file):
                    logger.warning('{} disappeared during run', basename(file))
                    continue
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
