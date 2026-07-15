from agroia.tenancy import Role, UserContext


def make_context(role: Role) -> UserContext:
    return UserContext(
        tenant_id="demo-rancho",
        tenant_name="Rancho demo",
        user_id="demo-user",
        display_name="Demo",
        role=role,
    )


def test_owner_and_admin_can_manage_costs() -> None:
    assert make_context(Role.OWNER).can_manage_costs is True
    assert make_context(Role.ADMIN).can_manage_costs is True
    assert make_context(Role.ADVISOR).can_manage_costs is False
    assert make_context(Role.OPERATOR).can_manage_costs is False


def test_advisor_can_create_recommendations_without_tenant_configuration() -> None:
    advisor = make_context(Role.ADVISOR)

    assert advisor.can_create_recommendations is True
    assert advisor.can_configure_tenant is False
    assert advisor.can_record_operations is False


def test_operator_can_record_operations_only() -> None:
    operator = make_context(Role.OPERATOR)

    assert operator.can_record_operations is True
    assert operator.can_create_recommendations is False
    assert operator.can_configure_tenant is False
