from openfisca_us.model_api import *


class education_credit_phaseout(Variable):
    value_type = float
    entity = TaxUnit
    label = "Education credit phase-out"
    unit = "/1"
    documentation = "Percentage of the American Opportunity and Lifetime Learning credits which are phased out"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        education = parameters(period).irs.credits.education
        agi = tax_unit("adjusted_gross_income", period)
        is_joint = tax_unit("tax_unit_is_joint", period)
        phaseout_start = where(
            is_joint,
            education.phaseout.start.joint,
            education.phaseout.start.single,
        )
        phaseout_length = where(
            is_joint,
            education.phaseout.length.joint,
            education.phaseout.length.single,
        )
        excess_agi = max(0, agi - phaseout_start)
        return min_(1, excess_agi / phaseout_length)
