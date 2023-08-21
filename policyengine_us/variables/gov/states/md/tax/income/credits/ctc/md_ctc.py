from policyengine_us.model_api import *


class md_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Child Tax Credit"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
        "https://law.justia.com/codes/maryland/2022/tax-general/title-10/subtitle-7/section-10-751/"
    )
    defined_for = "md_ctc_eligible"

    def formula_2020(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.ctc
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        disabled = person("is_disabled", period)
        age_limit = where(
            disabled, p.age_threshold.disabled, p.age_threshold.main
        )
        meets_age_limit = person("age", period) < age_limit
        eligible = dependent & meets_age_limit
        eligible_children = tax_unit.sum(eligible)
        md_ctc = eligible_children * p.amount
        if p.reduced_by_federal_credit:
            federal_ctc = tax_unit("ctc", period)
            return max_(md_ctc - federal_ctc, 0)
        return md_ctc
