import click


@click.command('publish-build')
@click.pass_obj
def cli(environment):
    """assemble the wheel to be published to pypi"""
    command = f"docker compose --profile publish run"
    environment.run_on_host(command)