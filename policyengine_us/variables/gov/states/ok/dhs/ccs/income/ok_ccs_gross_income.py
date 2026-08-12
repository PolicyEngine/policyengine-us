from policyengine_us.model_api import *


class ok_ccs_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Oklahoma Child Care Subsidy gross countable income"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-40-7-11"

    def formula(spm_unit, period, parameters):
        sources = parameters(period).gov.states.ok.dhs.ccs.income.sources
        person = spm_unit.members
        partnership_s_corp_income = max_(person("partnership_s_corp_income", period), 0)
        return add(spm_unit, period, sources) + spm_unit.sum(partnership_s_corp_income)
