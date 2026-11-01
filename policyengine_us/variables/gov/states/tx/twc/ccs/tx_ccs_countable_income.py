from policyengine_us.model_api import *


class tx_ccs_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Texas Child Care Services countable income"
    reference = "https://texas-sos.appianportalsgov.com/rules-and-meetings?interface=VIEW_TAC_SUMMARY&recordId=210290"
    unit = USD
    defined_for = StateCode.TX

    adds = "gov.states.tx.twc.ccs.income.sources"
