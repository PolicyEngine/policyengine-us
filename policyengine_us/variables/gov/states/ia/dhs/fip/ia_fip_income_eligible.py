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
        p = parameters(period).gov.states.ia.dhs.fip.income

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

        # Test 1: Gross income <= 185% of standard of need (applies to both)
        gross_income = spm_unit("ia_fip_gross_income", period)
        standard_of_need = spm_unit("ia_fip_standard_of_need", period)
        gross_income_limit = standard_of_need * p.gross_income_limit_percent
        gross_income_eligible = gross_income <= gross_income_limit

        # Test 2: Net income < standard of need (initial eligibility only)
        # Uses 20% earned income deduction but NOT the 58% work incentive disregard
        gross_earned_income = add(
            spm_unit, period, ["tanf_gross_earned_income"]
        )
        earned_income_deduction = (
            gross_earned_income * p.earned_income_deduction
        )
        net_income = gross_income - earned_income_deduction
        net_income_eligible = net_income < standard_of_need

        # Test 3: Countable income < payment standard (applies to both)
        # Uses both 20% deduction AND 58% work incentive disregard
        countable_income = spm_unit("ia_fip_countable_income", period)
        payment_standard = spm_unit("ia_fip_payment_standard", period)
        payment_standard_eligible = countable_income < payment_standard

        # Apply appropriate tests based on enrollment status
        return where(
            is_enrolled,
            # Continuing eligibility: tests 1 and 3 only
            gross_income_eligible & payment_standard_eligible,
            # Initial eligibility: all three tests
            gross_income_eligible
            & net_income_eligible
            & payment_standard_eligible,
        )
