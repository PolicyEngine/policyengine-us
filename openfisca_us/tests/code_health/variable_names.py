GROUP_ENTITY_NAMES = (
    "tax_unit",
    "spm_unit",
    "family",
    "household",
)


def test_variable_names():
    from openfisca_us import CountryTaxBenefitSystem

    system = CountryTaxBenefitSystem()
    for instance in system.variables.values():
        variable = type(instance)
        assert (
            variable.__name__.islower()
        ), f"{variable.__name__} is not all lowercase"
        if variable.entity.key in GROUP_ENTITY_NAMES:
            pass
            # assert variable.__name__[:len(variable.entity.key)] == variable.entity.key, f"{variable.__name__} does not begin with the specified group entity"
