from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_streamlined_eitc() -> Reform:
    """
    Streamlined EITC Reform:
    - Single schedule for all filers with dependent children (1+ children)
    - Maximum credit varies by filing status: single vs married

    To model the full policy, set these existing IRS parameters:
    - gov.irs.credits.eitc.phase_in_rate (34% for 1+ children)
    - gov.irs.credits.eitc.phase_out.start (phase-out start for single)
    - gov.irs.credits.eitc.phase_out.joint_bonus (additional amount for married)
    - gov.irs.credits.eitc.phase_out.rate (phase-out rate)

    This reform adds:
    - gov.contrib.streamlined_eitc.max.single (max credit for single/HOH)
    - gov.contrib.streamlined_eitc.max.joint (max credit for married filing jointly)
    """

    class eitc_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum EITC"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD

        def formula(tax_unit, period, parameters):
            child_count = tax_unit("eitc_child_count", period)
            p = parameters(period).gov.contrib.streamlined_eitc
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            return where(
                joint,
                p.max.joint.calc(child_count),
                p.max.single.calc(child_count),
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(eitc_maximum)

    return reform


def create_streamlined_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_streamlined_eitc()

    p = parameters.gov.contrib.streamlined_eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_streamlined_eitc()
    else:
        return None


streamlined_eitc = create_streamlined_eitc_reform(None, None, bypass=True)
