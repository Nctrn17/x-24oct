# Repare les textes mal encodes par PowerShell (UTF-8 relu en cp850 : "├®" au lieu de "é").
def reparer(t: str) -> str:
    try:
        return t.encode("cp850").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return t
