from policyengine_us.model_api import *


class tx_medicaid_ltss_qit_opening_month_exclusion_applies(Variable):
    value_type = bool
    entity = Person
    label = "Texas Medicaid LTSS QIT opening-month whole-source exclusion applies"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Derives the Texas opening-month whole-source income exclusion "
        "from the trust's opening year and month, a positive covered-source "
        "deposit, and verification of subsequent full deposits. A partial "
        "opening deposit can cover multiple identified sources, so the "
        "positive deposit condition combines earned and unearned source "
        "components. Covered deposited components cannot exceed either "
        "the covered source or the actual valid deposits. Other months "
        "and states continue to exclude actual valid deposits only."
    )
    reference = "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust"

    def formula(person, period, parameters):
        state = person.household("state_code", period)
        states = state.possible_values
        opening_year = person("medicaid_ltss_qit_opening_year", period)
        opening_month = person("medicaid_ltss_qit_opening_month", period)
        verified = person("medicaid_ltss_qit_subsequent_full_deposits_verified", period)

        earned = max_(person("medicaid_ltss_gross_earned_income", period), 0)
        covered_earned = min_(
            max_(person("medicaid_ltss_qit_covered_earned_income", period), 0),
            earned,
        )
        earned_deposits = min_(
            max_(person("medicaid_ltss_earned_income_deposited_to_qit", period), 0),
            earned,
        )
        covered_earned_deposits = min_(
            max_(
                person("medicaid_ltss_qit_covered_earned_income_deposited", period), 0
            ),
            min_(covered_earned, earned_deposits),
        )

        unearned = max_(person("medicaid_ltss_gross_unearned_income", period), 0)
        covered_unearned = min_(
            max_(person("medicaid_ltss_qit_covered_unearned_income", period), 0),
            unearned,
        )
        unearned_deposits = min_(
            max_(person("medicaid_ltss_unearned_income_deposited_to_qit", period), 0),
            unearned,
        )
        covered_unearned_deposits = min_(
            max_(
                person("medicaid_ltss_qit_covered_unearned_income_deposited", period),
                0,
            ),
            min_(covered_unearned, unearned_deposits),
        )
        positive_covered_deposit = (
            covered_earned_deposits + covered_unearned_deposits
        ) > 0
        return (
            (state == states.TX)
            & (opening_year == period.start.year)
            & (opening_month == period.start.month)
            & verified
            & positive_covered_deposit
        )
