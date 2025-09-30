from policyengine_us.model_api import *


class tx_ottanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Texas OTTANF income test"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2420-eligibility-requirements",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-802",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # OTTANF income test: gross income ≤ 200% of Federal Poverty Level
        # Per handbook: "Do not allow any income deductions"
        # Uses simple gross income (no work expense, no disregards, no deductions)

        # Gross income = all earned + unearned income (no deductions)
        gross_income = add(
            spm_unit,
            period,
            ["tx_tanf_gross_earned_income", "tx_tanf_gross_unearned_income"],
        )

        # Get FPL for household
        poverty_guideline = spm_unit("tx_tanf_fpg", period)

        # OTTANF income limit: 200% of FPL
        p = parameters(period).gov.states.tx.tanf.ottanf
        income_limit = poverty_guideline * p.income_limit_percentage

        return gross_income <= income_limit
