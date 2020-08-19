from os import makedirs
from os.path import basename
from sys import argv, stderr
from time import sleep

from click import Choice as CHOICE, INT, Path as PATH, STRING, command, option

from loguru import logger

from notifiers.logging import NotificationHandler

from .harvestr import Harvestr


@command()
@option('--source',
        '-s',
        type=PATH(exists=True,
                  file_okay=False,
                  dir_okay=True,
                  writable=False,
                  readable=True,
                  resolve_path=True,
                  allow_dash=False),
        envvar='HARVESTR_SOURCE',
        required=True,
        multiple=True)
@option('--target',
        '-t',
        type=PATH(exists=False,
                  file_okay=False,
                  dir_okay=True,
                  writable=True,
                  readable=True,
                  resolve_path=True,
                  allow_dash=False),
        envvar='HARVESTR_TARGET',
        required=True)
@option('--recycle',
        '-r',
        type=PATH(exists=False,
                  file_okay=False,
                  dir_okay=True,
                  writable=True,
                  readable=True,
                  resolve_path=True,
                  allow_dash=False),
        envvar='HARVESTR_RECYCLE',
        required=True)
@option('--dry-run',
        '-d',
        envvar='HARVESTR_DRY_RUN',
        is_flag=True)
@option('--sleep-time',
        type=INT,
        envvar='HARVESTR_SLEEP_TIME',
        default=5)
@option('--log-level',
        type=CHOICE(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'SUCCESS', 'TRACE'],
                    case_sensitive=False),
        envvar='HARVESTR_LOG_LEVEL',
        default='DEBUG')
@option('--slack-webhook',
        type=STRING,
        envvar='SLACK_WEBHOOK',
        default=None)
@option('--slack-username',
        type=STRING,
        envvar='SLACK_USERNAME',
        default='Harvestr')
@option('--slack-format',
        type=STRING,
        envvar='SLACK_FORMAT',
        default='{message}')
def main(source, target, recycle, dry_run, sleep_time, log_level, slack_webhook, slack_username, slack_format):
    logger.remove()
    logger.add(stderr, level=log_level)

    if slack_webhook:
        params = {
            "username": slack_username,
            "webhook_url": slack_webhook
        }
        slack = NotificationHandler("slack", defaults=params)
        logger.add(slack, format=slack_format, level="SUCCESS")

    logger.success(f'{basename(argv[0])} Started')
    logger.info('  --source "{}"', ':'.join(source))
    logger.info('  --target "{}"', target)
    logger.info('  --recycle "{}"', recycle)
    if dry_run:
        logger.info('  --dry-run')
    logger.info('  --sleep-time {}', sleep_time)
    logger.info('  --log-level "{}"', log_level)
    logger.info('  --slack-webhook "{}"', slack_webhook)
    logger.info('  --slack-username "{}"', slack_username)
    logger.info('  --slack-format "{}"', slack_format)

    makedirs(target, exist_ok=True)
    makedirs(recycle, exist_ok=True)
    h = Harvestr(target, recycle, source, dry_run=dry_run)
    while True:
        logger.debug(f'Sleeping {sleep_time} seconds')
        sleep(sleep_time)
        h.main()


if __name__ == "__main__":
    main()
