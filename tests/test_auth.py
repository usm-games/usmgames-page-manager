from usmgpm.resources.auth import generate_username


def test_username():
    assert generate_username('usmgpm', []) == 'usmgpm'
    assert generate_username('usmgpm', ['usmgpm']) == 'usmgpm.1'
    assert generate_username('Nombre Apellido', []) == 'nombre.apellido'
    assert generate_username('Ñombre Apellido', []) == 'nombre.apellido'
    assert generate_username('Ñombre Apellido', ['nombre.apellido']) == 'nombre.apellido.1'
