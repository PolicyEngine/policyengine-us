from policyengine_us.model_api import *


class tx_medicaid_ltss_countable_interest_and_dividends(Variable):
    value_type = float
    entity = Person
    label = "Texas Medicaid LTSS countable interest and dividends from other resources"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Monthly interest and dividends included in the investment-income "
        "leaves that remain countable under MEPD E-3331.3 because they arise "
        "from resources outside E-3331.1 and E-3331.2. Report the amount "
        "countable under the handbook's treatment of those other resources. "
        "The default assumes the reported investment income arises from "
        "fully countable resources or the specified excluded resources. "
        "This is a subset of gross investment receipts, not additional income."
    )
    reference = "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/e-3300-sources-unearned-income"
