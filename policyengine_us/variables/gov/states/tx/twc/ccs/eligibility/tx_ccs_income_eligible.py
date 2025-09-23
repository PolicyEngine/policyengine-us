from policyengine_us.model_api import *


class tx_ccs_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas CCS income eligible"
    definition_period = MONTH
    reference = "http://txrules.elaws.us/rule/title40_chapter809_sec.809.41"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs
        # Get monthly countable income
        monthly_income = spm_unit("tx_ccs_countable_income", period)
        # Calculate monthly SMI limit
        smi = spm_unit("hhs_smi", period)
        income_limit = smi * p.income.smi_rate
        return monthly_income <= income_limit
