from policyengine_us.model_api import *


class ut_at_home_parent_credit_eligibility(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Utah at-home parent credit eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ut.tax.income.credits.at_home_parent

        parent_qualifies = (
            person("irs_employment_income", period)
            + person("self_employment_income", period)
        ) < p.parent_max_earnings
        one_parent_qualifies = tax_unit.sum(parent_qualifies) > 0
        tax_unit_qualifies = (
            tax_unit("adjusted_gross_income", period) < p.max_agi
        )

        return one_parent_qualifies * tax_unit_qualifies
