import click


@click.command("refactor")
@click.option(
    "--all",
    "-a",
    "all_",
    is_flag=True,
    default=False,
    help="refactor all code in the project regardless of changes",
)
@click.pass_obj
def cli(environment, all_: bool):
    """refactors all code committed to the current branch that differs from main"""
    refactor_targets = "."
    if not all_:
        changed_files_cmd = "git diff --diff-filter=d --name-only $(git merge-base HEAD origin/main) HEAD | grep -E '\.py$'"
        _, raw_targets, _ = environment.run_on_host(
            changed_files_cmd, capture_output=True
        )
        # exclude .palm/ from refactor targets
        filtered_targets = [
            target
            for target in raw_targets.split("\n")
            if not target.startswith(".palm/")
        ]
        refactor_targets = " ".join(filtered_targets)
    if not refactor_targets:
        click.echo(
            click.style(
                "No files eligible for refactoring, have you committed all your changes?",
                fg="yellow",
            )
        )
        return
    click.echo(
        f"\nRefactoring {click.style(('updated' if not all_ else 'all'),fg='yellow')} code...\n"
    )
    environment.run_in_docker(
        f"cd /app && black {refactor_targets} && prospector -I migrations {refactor_targets}"
    )
