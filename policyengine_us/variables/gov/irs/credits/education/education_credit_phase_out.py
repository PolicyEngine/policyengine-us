from policyengine_us.model_api import *


class education_credit_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Education credit phase-out"
    unit = "/1"
    documentation = "Percentage of the American Opportunity and Lifetime Learning credits which are phased out"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        education = parameters(period).gov.irs.credits.education
        # 26 U.S.C. 25A(d)(2): modified adjusted gross income adds back
        # income excluded under sections 911, 931 and 933.
        magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        is_joint = tax_unit("tax_unit_is_joint", period)
        phase_out_start = where(
            is_joint,
            education.phase_out.start.joint,
            education.phase_out.start.single,
        )
        phase_out_length = where(
            is_joint,
            education.phase_out.length.joint,
            education.phase_out.length.single,
        )
        excess_magi = max_(0, magi - phase_out_start)
        return min_(1, excess_magi / phase_out_length)
