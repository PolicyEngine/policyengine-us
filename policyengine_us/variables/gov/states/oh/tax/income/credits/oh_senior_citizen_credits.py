from policyengine_us.model_api import *


class oh_senior_citizen_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio senior citizen credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.055",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age_threshold = parameters(period).gov.states.oh.tax.income.credits.senior_citizen.age_threshold
        agi_cap = parameters(period).gov.states.oh.tax.income.credits.senior_citizen.agi_cap
        credit_amount = parameters(period).gov.states.oh.tax.income.credits.senior_citizen.credit_amount
        has_not_taken_lump_sum_distribution = tax_unit("oh_has_not_taken_oh_lump_sum_credits", period)

        age = person("age", period)
        any_over_65 = sum(age > age_threshold) >= 1
        agi = tax_unit("oh_adjusted_gross_income", period)
        under_agi_cap = agi < agi_cap
        return any_over_65 * under_agi_cap * credit_amount * has_not_taken_lump_sum_distribution
