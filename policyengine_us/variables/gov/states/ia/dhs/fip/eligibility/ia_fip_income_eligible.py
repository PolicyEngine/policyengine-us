from policyengine_us.model_api import *


class ia_fip_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP income eligible"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=19",
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Code-r-441-41.27",
    )

    def formula(spm_unit, period, parameters):
        # Iowa FIP has different income tests for initial vs continuing eligibility
        # per IAC 441-41.27(239B):
        #
        # Initial eligibility (3-step process):
        #   1. Gross income <= 185% of standard of need
        #   2. Net income (after 20% earned income deduction) < standard of need
        #   3. Countable income (after 58% work incentive disregard) < payment standard
        #
        # Continuing eligibility (2-step process):
        #   1. Gross income <= 185% of standard of need
        #   2. Countable income (after 58% work incentive disregard) < payment standard
        #
        # The work incentive disregard does NOT apply to the net income test (step 2)
        # for initial eligibility. Continuing recipients skip step 2 entirely.

        is_enrolled = spm_unit("is_tanf_enrolled", period)
        gross_income_eligible = spm_unit(
            "ia_fip_gross_income_eligible", period
        )
        net_income_eligible = spm_unit("ia_fip_net_income_eligible", period)
        countable_income_eligible = spm_unit(
            "ia_fip_countable_income_eligible", period
        )

        return where(
            is_enrolled,
            gross_income_eligible & countable_income_eligible,
            gross_income_eligible
            & net_income_eligible
            & countable_income_eligible,
        )
