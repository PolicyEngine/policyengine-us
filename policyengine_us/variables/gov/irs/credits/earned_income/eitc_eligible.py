from policyengine_us.model_api import *


class eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_child = tax_unit.any(person("is_child", period))
        age = person("age", period)
        eitc = parameters.gov.irs.credits.eitc(period)
        min_age = parameters.gov.irs.credits.eitc.eligibility.age.min(period)
        meets_age_requirements = (age >= min_age) & (
            age <= eitc.eligibility.age.max
        )
        inv_income_sources = eitc.eligibility.counted_inv_income
        investment_income = (
            add(tax_unit, period, inv_income_sources)
            + max_(0, tax_unit("c01000", period))
            + max_(
                0,
                tax_unit("tax_unit_rental_income", period)
                - tax_unit("tax_unit_partnership_s_corp_income", period),
            )
        )
        inv_income_disqualified = (
            investment_income > eitc.phase_out.max_investment_income
        )
        eligible = has_child | tax_unit.any(meets_age_requirements)
        return eligible & ~inv_income_disqualified
