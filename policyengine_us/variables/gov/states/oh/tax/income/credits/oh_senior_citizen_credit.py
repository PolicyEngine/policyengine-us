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
        head = person("is_tax_unit_head", period)
        head_has_not_taken_lump_sum_distribution = (
            ~person("oh_has_taken_oh_lump_sum_credits", period) * head
        )
        age_head = tax_unit("age_head", period)
        elderly_head = age_head >= p.age_threshold
        eligible_head = (
            tax_unit.any(head_has_not_taken_lump_sum_distribution)
            & elderly_head
        )
        agi = tax_unit("oh_modified_agi", period)
        exemptions = tax_unit("oh_personal_exemptions", period)
        applicable_income = max_(agi - exemptions, 0)
        credit_amount = p.amount.calc(applicable_income)
        return eligible_head * credit_amount
