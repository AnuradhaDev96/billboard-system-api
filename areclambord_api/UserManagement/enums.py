from enum import Enum


class BillboardUserType(Enum):
    CUSTOMER = "Customer"
    VENDOR = "Vendor"
    ADMIN = "Admin"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


# billboard_enums
class BillboardType(Enum):
    DIGITAL = "Digital"
    LARGE = "Large"
    MEDIUM = "Medium"
    SMALL = "Small"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


# advertisement enums
class AdvertisementPackageType(Enum):
    GOLD = "Gold"
    PLATINUM = "Platinum"
    SILVER = "Silver"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ValidDatesForAdPackage(Enum):
    D_GOLD = "Gold"
    D_PLATINUM = "Platinum"
    D_SILVER = "Silver"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
