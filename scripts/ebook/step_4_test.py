"""Unit Tests."""  # noqa: INP001

from step_4 import convert_parsel


def test_convert_parsel() -> None:
    """Test convert_parsel."""
    assert convert_parsel("foo") == "foo"
    # s
    assert convert_parsel("house") == "housse"
    assert convert_parsel("Special") == "Sspecial"
    # ss and ß
    assert convert_parsel("Professor") == "Professsor"
    assert convert_parsel("muß") == "musss"
    # z
    assert convert_parsel("zero") == "zzero"
    assert convert_parsel("Zero") == "Zzero"
    # zz
    assert convert_parsel("puzzled") == "puzzzled"
    # x -> xs
    assert convert_parsel("Bellatrix") == "Bellatrixs"

    # combined
    assert convert_parsel("expression") == "exspresssion"
    assert convert_parsel("Salazar") == "Ssalazzar"
