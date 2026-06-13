from agroia import application


def test_run_bootstraps_and_renders_selected_page(monkeypatch) -> None:
    ctx = object()
    rendered_contexts = []

    monkeypatch.setattr(application, "bootstrap_app", lambda: ctx)
    monkeypatch.setattr(
        application,
        "render_selected_page",
        rendered_contexts.append,
    )

    application.run()

    assert rendered_contexts == [ctx]
