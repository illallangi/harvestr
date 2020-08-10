import schedule
import time
import click
from .harvestr import Harvestr

@click.command(context_settings={"auto_envvar_prefix": "HARVESTR"})
@click.option('--target',  '-t', type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True, allow_dash=False), required=True)
@click.option('--recycle', '-r', type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True, allow_dash=False))
@click.option('--source',  '-s', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True, resolve_path=True, allow_dash=False), required=True, multiple=True)
@click.option('--dry-run', '-d', is_flag=True)
@click.option('--verbose', '-v', is_flag=True)
def main(target, dry_run, verbose, recycle=None, source=None):
  os.makedirs(target, exist_ok=True)
  os.makedirs(recycle, exist_ok=True)
  h = Harvestr(target, recycle, source, dry_run = dry_run, verbose = verbose)
  h.main()
  schedule.every(1).minute.do(h.main)
  next_run = None
  while True:
    if (next_run != schedule.next_run()):
      next_run = schedule.next_run()
      click.echo(f'Will run again in {round(schedule.idle_seconds(), 0)} seconds, at {next_run}.')
    time.sleep(1)
    schedule.run_pending()

if __name__ == "__main__":
  main()
