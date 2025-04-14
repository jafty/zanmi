# zanmi_project/tests/test_imports.py
def test_import_user():
    from domain.user import User
    assert User is not None
