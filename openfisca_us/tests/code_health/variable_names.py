GROUP_ENTITY_NAMES = (
    "tax_unit",
    "spm_unit",
    "family",
    "household",
)


def test_variable_names():
    from openfisca_us import CountryTaxBenefitSystem
    from openfisca_us.model_api import STATES

    system = CountryTaxBenefitSystem()
    for instance in system.variables.values():
        variable = type(instance)
        if variable.__name__ in STATES:
            # State codes are allowed
            continue
        assert (
            variable.__name__.islower()
        ), f"{variable.__name__} is not all lowercase"
