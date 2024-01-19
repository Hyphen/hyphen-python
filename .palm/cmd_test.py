import click


@click.command('test')
@click.option("--failed", is_flag=True, help="Run only failed tests")
@click.pass_obj
def cli(environment, failed:bool):
    """test"""
    click.echo("running pytest...")

    failed_cmd = '--lf --last-failed-no-failures none' if failed else ''

    environment.run_in_docker(f"pytest tests {failed_cmd}")