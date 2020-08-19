from os import makedirs
from sys import stderr
from time import sleep

import click

from loguru import logger

from .harvestr import Harvestr


@click.command(context_settings={"auto_envvar_prefix": "HARVESTR"})
@click.option('--target', '-t', type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True, allow_dash=False), required=True)
@click.option('--recycle', '-r', type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True, allow_dash=False), required=True)
@click.option('--source', '-s', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True, resolve_path=True, allow_dash=False), required=True, multiple=True)
@click.option('--dry-run', '-d', is_flag=True)
@click.option('--log-level',
              type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'SUCCESS', 'TRACE'],
                                case_sensitive=False),
              envvar='HARVESTR_LOG_LEVEL',
              default='DEBUG')
@click.option('--sleep-time',
              type=click.INT,
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
