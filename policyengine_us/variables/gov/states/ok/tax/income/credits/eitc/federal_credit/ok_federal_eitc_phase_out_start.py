from policyengine_us.model_api import *


class ok_federal_eitc_phase_out_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC phase-out start for the Oklahoma EITC computation"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        count_children = tax_unit("eitc_child_count", period)
        eitc = parameters(f"2020-01-01").gov.irs.credits.eitc
        is_joint = tax_unit("tax_unit_is_joint", period)
        joint_bonus = eitc.phase_out.joint_bonus.calc(count_children)
        phase_out_start = eitc.phase_out.start.calc(count_children)
        return phase_out_start + is_joint * joint_bonus
