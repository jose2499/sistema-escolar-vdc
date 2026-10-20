from escolar.domain.seguridad import hash_password, verificar_password


def test_el_hash_no_guarda_la_clave_en_texto_plano():
    assert "clave123" not in hash_password("clave123")


def test_verifica_una_clave_correcta():
    almacenado = hash_password("clave123", iteraciones=1000)
    assert verificar_password("clave123", almacenado) is True


def test_rechaza_una_clave_incorrecta():
    almacenado = hash_password("clave123", iteraciones=1000)
    assert verificar_password("otra-clave", almacenado) is False


def test_la_misma_clave_genera_hashes_distintos_por_el_salt():
    assert hash_password("clave123", iteraciones=1000) != hash_password(
        "clave123", iteraciones=1000
    )


def test_un_hash_con_formato_corrupto_no_verifica():
    assert verificar_password("clave123", "basura") is False
