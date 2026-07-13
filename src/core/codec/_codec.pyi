def decode(
    data: bytes | bytearray,
    extra: dict[str, str] | None = None,
    trans: dict[str, str] | None = None,
) -> str: ...
def encode(
    text: str,
    mask: bytes | bytearray,
    extra: dict[str, str] | None = None,
    trans: dict[str, str] | None = None,
) -> bytearray: ...
def encode_var(
    text: str,
    extra: dict[str, str] | None = None,
    trans: dict[str, str] | None = None,
) -> tuple[bytes, int]: ...
