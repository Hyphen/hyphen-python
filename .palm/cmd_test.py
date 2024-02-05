from typing import Optional
import click


@click.command('test')
@click.option("--failed", is_flag=True, help="Run only failed tests")
@click.option("-k", help="run matching tests for PyTest query language")
@click.pass_obj
def cli(environment, k:Optional[str], failed:bool):
    """test"""
    click.echo("running pytest...")

    failed_cmd = '--lf --last-failed-no-failures none' if failed else ''
    k = f'-k "{k}" ' if k else ''
    environment.run_in_docker(f"pytest tests {k}{failed_cmd}")