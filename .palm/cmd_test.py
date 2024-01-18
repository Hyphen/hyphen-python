import click


@click.command('test')
@click.pass_obj
def cli(environment):
    """test"""
    click.echo("running pytest...")
    environment.run_in_docker("pytest tests")