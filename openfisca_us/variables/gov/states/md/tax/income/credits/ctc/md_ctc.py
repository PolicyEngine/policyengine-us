from openfisca_us.model_api import *


class md_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CTC"
    definition_period = YEAR
    unit = USD
    documentation = "Maryland Child Tax Credit"
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.ctc
        income_eligible = (
            tax_unit("adjusted_gross_income", period) <= p.agi_cap
        )
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        disabled = person("is_disabled", period)
        meets_age_limit = person("age", period) < p.age_limit
        eligible_child = dependent & disabled & meets_age_limit
        eligible_children = tax_unit.sum(eligible_child)
        return income_eligible * eligible_children * p.amount
