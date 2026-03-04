from enum import Enum


class RoleEnum(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    SUPERADMIN = "superadmin"
