import pytest

from policyengine_us import CountryTaxBenefitSystem


SYSTEM = CountryTaxBenefitSystem()


def test_dc_tanf_work_sanction_rate_parameter_schedule():
    # Keep the ongoing sanction behavior in YAML, but pin the 2026-10 rate step
    # here until the YAML runner can safely cover this future monthly period.
    assert (
        SYSTEM.parameters(
            "2026-10"
        ).gov.states.dc.dhs.tanf.work_requirement.sanction.rate
    ) == pytest.approx(0.25)
