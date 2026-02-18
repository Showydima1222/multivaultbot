from dataclasses import dataclass

@dataclass
class Vault:
    name: str = ""
    course: float = 0.0
    nominal: int = 0
    char_code: str = ""

@dataclass
class Vaults:
    vaults: dict[str, Vault]
    avaible_vaults: set[str]
    refreshed_at: int