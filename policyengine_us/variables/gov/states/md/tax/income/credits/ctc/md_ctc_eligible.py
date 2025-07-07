from policyengine_us.model_api import *


class md_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Maryland Child Tax Credit"
    definition_period = YEAR
    reference = [
        "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child",
        "https://law.justia.com/codes/maryland/2022/tax-general/title-10/subtitle-7/section-10-751/",
        "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=169",  # Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.ctc
        agi = tax_unit("adjusted_gross_income", period)

        # When phase-out applies, eligibility is based on having eligible children
        # (phase-out is handled in the credit amount calculation)
        if p.phase_out.applies:
            person = tax_unit.members
            dependent = person("is_tax_unit_dependent", period)
            disabled = person("is_disabled", period)
            age_limit = where(
                disabled, p.age_threshold.disabled, p.age_threshold.main
            )
            meets_age_limit = person("age", period) < age_limit
            eligible = dependent & meets_age_limit
            return tax_unit.sum(eligible) > 0

        # When phase-out does not apply, use old logic (hard adjusted gross income cutoff)
        return agi <= p.agi_cap
