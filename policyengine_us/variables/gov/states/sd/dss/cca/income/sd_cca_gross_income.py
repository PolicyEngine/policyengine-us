from policyengine_us.model_api import *


class sd_cca_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "South Dakota CCA gross countable income"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=10"
    )
    adds = "gov.states.sd.dss.cca.income.sources"
