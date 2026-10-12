from policyengine_us.model_api import *


class id_iccp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Income eligible for the Idaho Child Care Program"
    defined_for = StateCode.ID
    reference = "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=7"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.iccp.income
        countable_income = spm_unit("id_iccp_countable_income", period)
        enrolled = spm_unit("id_iccp_enrolled", period)
        initial_limit = (
            spm_unit("spm_unit_fpg", period) * p.fpl_rate.initial_eligibility
        )
        continuing_limit = spm_unit("hhs_smi", period) * p.smi_rate.continuing
        return countable_income <= where(enrolled, continuing_limit, initial_limit)
