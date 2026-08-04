from policyengine_us.model_api import *


class mo_ccs_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri Child Care Subsidy countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MO
    reference = "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-050"

    adds = "gov.states.mo.dese.ccs.income.countable_income.sources"
