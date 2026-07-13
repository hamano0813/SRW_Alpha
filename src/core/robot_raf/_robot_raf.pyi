def parse(
    data: bytes | bytearray,
    extra: dict[str, str] | None = None,
    trans: dict[str, str] | None = None,
) -> dict: ...
def build(
    data: dict,
    extra: dict[str, str] | None = None,
    trans: dict[str, str] | None = None,
) -> bytearray: ...
