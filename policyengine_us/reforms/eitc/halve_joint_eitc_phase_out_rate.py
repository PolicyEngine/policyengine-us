from policyengine_us.model_api import *


def create_halve_joint_eitc_phase_out_rate() -> Reform:
    class eitc_phase_out_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-out rate"
        unit = USD
        documentation = "Percentage of earnings above the phase-out threshold that reduce the EITC."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            eitc = parameters(period).gov.irs.credits.eitc
            num_children = tax_unit("eitc_child_count", period)
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            base_rate = eitc.phase_out.rate.calc(num_children)
            return where(joint, base_rate / 2, base_rate)

    class reform(Reform):
        def apply(self):
            self.update_variable(eitc_phase_out_rate)

    return reform


def create_halve_joint_eitc_phase_out_rate_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_halve_joint_eitc_phase_out_rate()

    p = parameters(period).gov.contrib.joint_eitc

    if p.in_effect:
        return create_halve_joint_eitc_phase_out_rate()
    else:
        return None


halve_joint_eitc_phase_out_rate = (
    create_halve_joint_eitc_phase_out_rate_reform(None, None, bypass=True)
)
