from policyengine_us.model_api import *


class tx_ccs_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Texas Child Care Services countable income"
    reference = "http://txrules.elaws.us/rule/title40_chapter809_sec.809.44"
    unit = USD
    defined_for = StateCode.TX

    adds = "gov.states.tx.twc.ccs.income.sources"
