from policyengine_us.model_api import *


class ut_at_home_parent_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah at-home parent credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        p = parameters(period).gov.states.ut.tax.income.credits.at_home_parent
        count_children = tax_unit.sum((age < p.max_child_age) & is_dependent)
        parent_qualifies = (
            person("irs_employment_income", period)
            + person("self_employment_income", period)
        ) < p.parent_max_earnings
        one_parent_qualifies = tax_unit.sum(parent_qualifies) > 0
        tax_unit_qualifies = (
            tax_unit("adjusted_gross_income", period) < p.max_agi
        )
        max_credit = (
            p.amount
            * count_children
            * one_parent_qualifies
            * tax_unit_qualifies
        )
        if p.refundable:
            limiting_liability = (
                tax_unit("ut_income_tax_before_credits", period)
                - tax_unit("ut_taxpayer_credit", period)
                - tax_unit("ut_eitc", period)
                - tax_unit("ut_retirement_credit", period)
                - tax_unit("ut_ss_benefits_credit", period)
            )
            return min_(max_credit, limiting_liability)
        return max_credit
