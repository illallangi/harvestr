from os import makedirs
from sys import stderr
from time import sleep

from click import Choice as CHOICE, INT, Path as PATH, command, option

from loguru import logger

from .harvestr import Harvestr


@command(context_settings={"auto_envvar_prefix": "HARVESTR"})
@option('--target', '-t', type=PATH(exists=False, file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True, allow_dash=False), required=True)
@option('--recycle', '-r', type=PATH(exists=False, file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True, allow_dash=False), required=True)
@option('--source', '-s', type=PATH(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True, resolve_path=True, allow_dash=False), required=True, multiple=True)
@option('--dry-run', '-d', is_flag=True)
@option('--log-level',
        type=CHOICE(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'SUCCESS', 'TRACE'],
                    case_sensitive=False),
        envvar='HARVESTR_LOG_LEVEL',
        default='DEBUG')
@option('--sleep-time',
        type=INT,
        envvar='HARVESTR_SLEEP_TIME',
        default=5)
def main(target, dry_run, recycle, source, sleep_time, log_level):
    logger.remove()
    logger.add(stderr, level=log_level)

    makedirs(target, exist_ok=True)
    makedirs(recycle, exist_ok=True)
    h = Harvestr(target, recycle, source, dry_run=dry_run)
    while True:
        logger.debug(f'Sleeping {sleep_time} seconds')
        sleep(sleep_time)
        h.main()


if __name__ == "__main__":
    main()
