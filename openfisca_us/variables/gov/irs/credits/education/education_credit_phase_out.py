from openfisca_us.model_api import *


class education_credit_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Education credit phase-out"
    unit = "/1"
    documentation = "Percentage of the American Opportunity and Lifetime Learning credits which are phased out"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        education = parameters(period).gov.irs.credits.education
        agi = tax_unit("adjusted_gross_income", period)
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
        excess_agi = max_(0, agi - phase_out_start)
        return min_(1, excess_agi / phase_out_length)
