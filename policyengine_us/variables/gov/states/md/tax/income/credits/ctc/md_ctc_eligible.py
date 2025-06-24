from policyengine_us.model_api import *


class md_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Maryland Child Tax Credit"
    definition_period = YEAR
    reference = [
        "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child",
        "https://law.justia.com/codes/maryland/2022/tax-general/title-10/subtitle-7/section-10-751/",
        "https://mgaleg.maryland.gov/Pubs/BudgetFiscal/2025rs-budget-docs-operating-cc-summary.pdf#page=17",  # FY 2025 Budget changes
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.ctc
        agi = tax_unit("adjusted_gross_income", period)

        # Starting in 2025, eligibility is based on having eligible children
        # (phase-out is handled in the credit amount calculation)
        if period.start.year >= 2025:
            person = tax_unit.members
            dependent = person("is_tax_unit_dependent", period)
            disabled = person("is_disabled", period)
            age_limit = where(
                disabled, p.age_threshold.disabled, p.age_threshold.main
            )
            meets_age_limit = person("age", period) < age_limit
            eligible = dependent & meets_age_limit
            has_eligible_children = tax_unit.sum(eligible) > 0
            return has_eligible_children

        # For years before 2025, use old logic (hard AGI cutoff)
        return agi <= p.agi_cap
