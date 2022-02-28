from atexit import register as atexit_register
from os import makedirs
from os.path import basename
from sys import argv, stderr
from time import sleep, time

from click import Choice as CHOICE, INT, Path as PATH, STRING, command, option

from loguru import logger

from notifiers.logging import NotificationHandler

from .harvestr import Harvestr

start_time = time()


def duration_human(seconds):
    seconds = int(round(seconds))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365.242199)

    minutes = int(minutes)
    hours = int(hours)
    days = int(days)
    years = int(years)

    duration = []
    if years > 0:
        duration.append('%d year' % years + 's' * (years != 1))
    else:
        if days > 0:
            duration.append('%d day' % days + 's' * (days != 1))
        if hours > 0:
            duration.append('%d hour' % hours + 's' * (hours != 1))
        if minutes > 0:
            duration.append('%d minute' % minutes + 's' * (minutes != 1))
        if seconds > 0:
            duration.append('%d second' % seconds + 's' * (seconds != 1))
    return ' '.join(duration)


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
@option('--exclude',
        '-e',
        type=STRING,
        envvar='HARVESTR_EXCLUDE',
        required=False)
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
@logger.catch
def main(source, target, recycle, exclude, dry_run, sleep_time, log_level, slack_webhook, slack_username, slack_format):
    logger.remove()
    logger.add(stderr, level=log_level)

    if slack_webhook:
        params = {
            "username": slack_username,
            "webhook_url": slack_webhook
        }
        slack = NotificationHandler("slack", defaults=params)
        logger.add(slack, format=slack_format, level="SUCCESS")

    logger.success('{} Started with {} source(s)', basename(argv[0]), len(source))
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

    try:
        makedirs(target, exist_ok=True)
        makedirs(recycle, exist_ok=True)
        h = Harvestr(target, recycle, source, exclude=[exclude] if exclude else None, dry_run=dry_run)
        while True:
            logger.debug(f'Sleeping {sleep_time} seconds')
            sleep(sleep_time)
            h.main()
    finally:
        lwt()


def lwt():
    logger.success('{} Exiting after {}', basename(argv[0]), duration_human(time() - start_time))


if __name__ == "__main__":
    atexit_register(lwt)
    main()
