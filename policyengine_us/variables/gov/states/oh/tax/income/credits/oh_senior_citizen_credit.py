from policyengine_us.model_api import *


class oh_senior_citizen_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio senior citizen credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.055",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits.senior_citizen
        person = tax_unit.members

        has_not_taken_lump_sum_distribution = person(
            "oh_has_not_taken_oh_lump_sum_credits", period
        )
        age = person("age", period)

        any_elderly = tax_unit.any(age >= p.age_threshold)
        credit_amount = p.agi_limit.calc(tax_unit("oh_agi", period))

        return (
            any_elderly * has_not_taken_lump_sum_distribution * credit_amount
        )
