import click
import os


@click.command("update-ci-env")
@click.option("--dry-run", is_flag=True, default=False)
@click.pass_obj
def cli(environment, dry_run: bool):
    """updates the CI .env file used for CI runs"""
    click.echo("Updating the CI .env file in Github to match your .env file...")
    if not os.getenv("GITHUB_HYPHEN_SET_ENV_PERSONAL_ACCESS_TOKEN"):
        click.echo(
            "Unable to find required Github personal access token at GITHUB_HYPHEN_SET_ENV_PERSONAL_ACCESS_TOKEN environment variable. See http://docs.localhost/how_tos/update_ci_envars_locally/ for how to do that."
        )
        return
    build = "docker build -t github_env --target=github . -f dockerfiles/Dockerfile"
    run_ = 'docker run --rm -e "GITHUB_TOKEN=${GITHUB_HYPHEN_SET_ENV_PERSONAL_ACCESS_TOKEN}" -v $PWD:/app/app github_env'
    if dry_run:
        run_ += " --dry-run"
    cleanup = "docker rmi github_env"
    for command in (
        build,
        run_,
        cleanup,
    ):
        environment.run_on_host(command)
    click.echo("\nGithub CI .env file has been updated to match yours!")
