from modules.auth import (
    TEMP_ALPHABET,
    generate_temp_password,
    hash_password,
    validate_new_password,
    verify_password,
)


def test_hash_e_verify_roundtrip():
    h = hash_password("minha-senha-123")
    assert h != "minha-senha-123"
    assert verify_password("minha-senha-123", h)


def test_senha_errada_rejeitada():
    h = hash_password("minha-senha-123")
    assert not verify_password("outra-senha", h)


def test_senha_temporaria_formato():
    temp = generate_temp_password()
    assert temp.startswith("copa-")
    sufixo = temp.removeprefix("copa-")
    assert len(sufixo) == 4
    assert all(c in TEMP_ALPHABET for c in sufixo)


def test_senha_temporaria_varia():
    geradas = {generate_temp_password() for _ in range(10)}
    assert len(geradas) > 1


def test_validate_nova_senha_curta():
    assert validate_new_password("abc", "abc") == "Senha deve ter pelo menos 6 caracteres."


def test_validate_confirmacao_diferente():
    assert validate_new_password("abcdef", "abcdeg") == "As senhas nao coincidem."


def test_validate_senha_ok():
    assert validate_new_password("abcdef", "abcdef") is None
