from policyengine_us.model_api import *


class wi_cts_large_group_net_income_limit(Variable):
    value_type = float
    entity = Family
    label = "Wisconsin CTS agency-verified large assistance group net income limit"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "Supply the agency-verified monthly net income limit, including any pregnancy allowance, when the assistance group has more than twelve people. The handbook publishes net limits only through size twelve. Zero means no verified limit has been supplied; the model cannot establish entitlement for that group."
