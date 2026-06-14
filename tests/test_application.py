import sys

from agroia import application


def test_run_forwards_cli_arguments_and_renders_selected_page(monkeypatch) -> None:
    ctx = object()
    bootstrap_arguments = []
    rendered_contexts = []

    monkeypatch.setattr(sys, "argv", ["app.py", "--demo"])
    monkeypatch.setattr(
        application,
        "bootstrap_app",
        lambda argv: bootstrap_arguments.append(argv) or ctx,
    )
    monkeypatch.setattr(
        application,
        "render_selected_page",
        rendered_contexts.append,
    )

    application.run()

    assert bootstrap_arguments == [["--demo"]]
    assert rendered_contexts == [ctx]
