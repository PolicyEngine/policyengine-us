from policyengine_us.model_api import *


class ri_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.RI
    reference = "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.2"

    adds = "gov.states.ri.dhs.ccap.income.countable_income.sources"
