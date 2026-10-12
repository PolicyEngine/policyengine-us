from policyengine_us.model_api import *


class wi_cts_buening_large_group_net_income_limit(Variable):
    value_type = float
    entity = Family
    label = "Wisconsin CTS agency-verified large Buening subgroup net income limit"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "Supply the agency-verified monthly net income limit, including any pregnancy allowance, when the Buening subgroup has more than twelve people. The handbook publishes net limits only through size twelve. Zero means no verified limit has been supplied; the model cannot establish entitlement for that group."
