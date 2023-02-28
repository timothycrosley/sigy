from __future__ import annotations

import sigy


def contact(name: str | None=None, email: str | None = None, id: int | None = None, *, y: str = "testing default") -> str:
    if not (name or email or id):
        raise ValueError("Must supply name, email, or id")
    if len(tuple(filter(lambda item: item is not None, (name, email, id)))) > 1:
        raise ValueError("Must only supply one of: name, email, or id")

    return f"{name or email or id} loaded succesfully"


@sigy.inject(prefix_="contact_", contact=contact, shadow_=True)
def user_information(contact: str, start: int) -> list[str]:
    return list(contact)[start:]
