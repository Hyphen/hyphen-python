import click


@click.command('test-versions')
@click.pass_obj
def cli(environment):
    """runs our tests against each supported version of python"""
    for classifier in range(6, 11):
            version = "3." + str(classifier)
            click.echo(f"Testing in python:{version}")
            environment.run_on_host(f"docker compose build --build-arg PYTHON_VERSION={version}")
            environment.run_on_host(f"palm test")