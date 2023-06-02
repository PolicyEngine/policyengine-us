from policyengine_us.model_api import *


class oh_retirement_income_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Retirement Income Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.retirement_income

        person = tax_unit.members
        pension_income = sum(person("pension_income", period))

        agi = tax_unit("oh_agi", period)
        has_not_taken_lump_sum_distribution = person(
            "oh_has_not_taken_oh_lump_sum_credits", period
        )

        eligible = agi < p.agi_cap and pension_income > 0
        return (
            p.agi_credit_amount.calc(agi)
            * eligible
            * has_not_taken_lump_sum_distribution
        )
