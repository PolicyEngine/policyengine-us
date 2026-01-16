from policyengine_us.model_api import *


class ca_child_care_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California child care income eligible"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/inforesources/calworks-child-care/program-eligibility"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.child_care.smi
        smi = spm_unit("ca_child_care_smi", period)
        income = spm_unit("spm_unit_market_income", period)
        return income <= smi * p.income_limit
