from .income_security_package import (
    income_security_package,
    create_income_security_package_reform,
)

# Keep individual reforms for backward compatibility but they all use the same implementation
baby_bonus_act = income_security_package
boost_act = income_security_package
end_child_poverty_act = income_security_package

__all__ = [
    "income_security_package",
    "create_income_security_package_reform",
    "baby_bonus_act",
    "boost_act",
    "end_child_poverty_act",
]
