from __future__ import annotations

import sigy


class Hi:

    def contact(self, name: str | None=None, email: str | None = None, id: int | None = None) -> str:
        if not (name or email or id):
            raise ValueError("Must supply name, email, or id")
        if len(tuple(filter(lambda item: item is not None, (name, email, id)))) > 1:
            raise ValueError("Must only supply one of: name, email, or id")
        
        return f"{name or email or id} loaded succesfully"

    @sigy.inject(contact=contact)
    def user_information(self, contact: str, start: int) -> list[str]:
        return list(contact)[start:]
