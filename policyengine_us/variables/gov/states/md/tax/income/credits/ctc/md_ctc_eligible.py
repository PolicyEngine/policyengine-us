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

        # Check for qualifying children (used in both paths)
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        disabled = person("is_disabled", period)
        age_limit = where(
            disabled, p.age_threshold.disabled, p.age_threshold.main
        )
        meets_age_limit = person("age", period) < age_limit
        qualifying_child = dependent & meets_age_limit
        has_qualifying_child = tax_unit.sum(qualifying_child) > 0

        # When phase-out applies (2025+): must have qualifying child AND AGI below max_agi
        # Per Worksheet 21C: "$24,000 or less" is eligible; "$24,001 or greater, STOP."
        # max_agi is set to 24_001 so that agi < 24_001 includes $24,000.
        agi_eligible = agi < p.phase_out.max_agi
        phase_out_eligible = has_qualifying_child & agi_eligible

        # When phase-out does not apply (pre-2025): use old logic (hard AGI cutoff)
        pre_phase_out_eligible = agi <= p.agi_cap

        return where(
            p.phase_out.applies, phase_out_eligible, pre_phase_out_eligible
        )
