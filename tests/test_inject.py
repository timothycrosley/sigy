from __future__ import annotations

import pytest

import sigy


def contact(name: str | None = None, email: str | None = None, id: int | None = None) -> str:
    """An example reusable function for the tests that represents contact loading based on one of many fields"""
    if not (name or email or id):
        raise ValueError("Must supply name, email, or id")
    if len(tuple(filter(lambda item: item is not None, (name, email, id)))) > 1:
        raise ValueError("Must only supply one of: name, email, or id")

    return f"{name or email or id} loaded succesfully"


def test_inject_basic():
    @sigy.inject(contact=contact)
    def user_information(contact: str, start: int = 0) -> list[str]:
        return contact[start:]

    assert user_information(contact="Timothy", start=1) == "imothy"
    assert user_information(name="Timothy", start=1) == "imothy loaded succesfully"
    assert (
        user_information(email="timothy.crosley@gmail.com", start=0)
        == "timothy.crosley@gmail.com loaded succesfully"
    )
    assert user_information(id="123", start=0) == "123 loaded succesfully"

    with pytest.raises(ValueError):
        user_information(id="123", name="timothy", start=0)
    with pytest.raises(ValueError):
        user_information(start=0)
    with pytest.raises(TypeError):
        user_information(non_existent=100, name="timothy", start=0)


def test_inject_prefix():
    """Testing injecting a function signature with a parameter prefix"""

    @sigy.inject(contact=contact, prefix_="contact_")
    def user_information(contact: str, start: int = 0) -> list[str]:
        return contact[start:]

    assert user_information(contact="Timothy", start=1) == "imothy"
    assert user_information(contact_name="Timothy", start=1) == "imothy loaded succesfully"
    assert (
        user_information(contact_email="timothy.crosley@gmail.com", start=0)
        == "timothy.crosley@gmail.com loaded succesfully"
    )
    assert user_information(contact_id="123", start=0) == "123 loaded succesfully"

    with pytest.raises(ValueError):
        user_information(contact_id="123", contact_name="timothy", start=0)
    with pytest.raises(ValueError):
        user_information(start=0)
    with pytest.raises(ValueError):
        user_information(name="timothy", start=0)


def test_inject_block():
    """Tests injecting with original parameter blocked"""

    @sigy.inject(contact=contact)
    def user_information(contact: str, start: int = 0) -> list[str]:
        return contact[start:]

    assert user_information(contact="Timothy")

    # blocking will make original parameter no longer directly reachable
    @sigy.inject(contact=contact, block_=True)
    def user_information(contact: str, start: int = 0) -> list[str]:
        return contact[start:]

    assert user_information(name="Timothy")
    with pytest.raises(TypeError):
        assert user_information(contact="Timothy")


def test_shadow():
    """Test to ensure shadowing works to hide the original parameter, while still leaving it accessible."""

    @sigy.inject(contact=contact)
    def user_information(contact: str, start: int = 0) -> list[str]:
        return contact[start:]

    assert "contact" in user_information.__annotations__

    # shadowing will make original parameter no longer visible but still reachable
    @sigy.inject(contact=contact, shadow_=True)
    def user_information(contact: str, start: int = 0) -> list[str]:
        return contact[start:]

    assert "contact" not in user_information.__annotations__
    assert user_information(contact="Timothy")
