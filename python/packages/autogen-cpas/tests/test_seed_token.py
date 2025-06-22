from cpas_autogen.seed_token import SeedToken


def test_generate_and_validate():
    data = {
        "id": "1",
        "model": "GPT",
        "timestamp": "2025",
        "alignment_profile": "CPAS",
        "hash": "abc",
    }
    token = SeedToken.generate(data)
    other = SeedToken.generate(data)
    assert token.validate(other)
    assert token.to_dict()["id"] == "1"


def test_validate_fails_on_different_tokens():
    data1 = {
        "id": "1",
        "model": "GPT",
        "timestamp": "2025",
        "alignment_profile": "CPAS",
        "hash": "abc",
    }
    data2 = {
        "id": "2",
        "model": "GPT",
        "timestamp": "2025",
        "alignment_profile": "CPAS",
        "hash": "abc",
    }
    token1 = SeedToken.generate(data1)
    token2 = SeedToken.generate(data2)
    assert not token1.validate(token2)
