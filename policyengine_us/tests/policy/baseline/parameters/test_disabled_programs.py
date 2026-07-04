from policyengine_us import CountryTaxBenefitSystem


def test_disabled_program_defaults_exclude_modeled_wic():
    system = CountryTaxBenefitSystem()

    disabled = list(system.parameters.simulation.disabled_programs("2024-01-01"))

    assert "spm_unit_wic" not in disabled
