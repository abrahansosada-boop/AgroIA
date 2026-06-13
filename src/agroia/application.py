from agroia.app_shell import bootstrap_app
from agroia.ui.router import render_selected_page


def run() -> None:
    ctx = bootstrap_app()
    render_selected_page(ctx)
