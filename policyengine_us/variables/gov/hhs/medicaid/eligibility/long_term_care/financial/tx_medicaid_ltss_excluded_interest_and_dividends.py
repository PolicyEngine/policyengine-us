from policyengine_us.model_api import *


class tx_medicaid_ltss_excluded_interest_and_dividends(Variable):
    value_type = float
    entity = Person
    label = "Texas Medicaid LTSS excluded interest and dividends"
    unit = USD
    definition_period = MONTH
    documentation = (
        "MEPD E-3331.1 excludes interest and dividends on fully countable "
        "resources from the eligibility budget regardless of amount or "
        "frequency; E-3331.2 excludes those on its specified excluded or "
        "partially excluded resources. E-3331.3 income that remains "
        "countable is reported separately and is not excluded here. "
        "This eligibility screen does not compute co-payment budgets. "
        "Other E-series exempt-income categories are outside this screen. "
        "Valid QIT deposits and covered sources must exclude these already "
        "exempt receipts to avoid counting the same exclusion twice."
    )
    reference = "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/e-3300-sources-unearned-income"

    def formula_2026_01_01(person, period, parameters):
        state = person.household("state_code", period)
        investment = max_(person("medicaid_ltss_interest_income", period), 0) + max_(
            person("medicaid_ltss_dividend_income", period), 0
        )
        countable = max_(
            person("tx_medicaid_ltss_countable_interest_and_dividends", period), 0
        )
        remaining = max_(
            person("medicaid_ltss_qit_adjusted_unearned_income", period), 0
        )
        return where(
            state == state.possible_values.TX,
            min_(max_(investment - countable, 0), remaining),
            0,
        )
