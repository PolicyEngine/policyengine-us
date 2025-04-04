from policyengine_us.model_api import *


class ma_eaedc_test_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC net income"
    unit = USD
    definition_period = MONTH
    defined_for = "ma_eaedc_eligible"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500"  # (B) step 2

    adds = [
        "ma_tcap_gross_unearned_income",
        "ma_eaedc_countable_earned_incomeC",
    ]
