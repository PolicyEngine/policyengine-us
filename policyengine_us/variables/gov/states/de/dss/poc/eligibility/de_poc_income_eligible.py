from policyengine_us.model_api import *


class de_poc_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Delaware Purchase of Care based on income"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = (
        "https://regulations.delaware.gov/AdminCode/title16/Department%20of%20Health%20and%20Social%20Services/Division%20of%20Social%20Services/11003.shtml",
        "https://dhss.delaware.gov/dss/childcr/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dss.poc.income
        countable_income = spm_unit("de_poc_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        smi = spm_unit("hhs_smi", period)
        enrolled = spm_unit("de_poc_enrolled", period)
        fpl_limit = where(
            enrolled,
            fpg * p.fpl_rate.redetermination,
            fpg * p.fpl_rate.initial_eligibility,
        )
        smi_limit = smi * p.smi_rate
        income_limit = min_(fpl_limit, smi_limit)
        return countable_income <= income_limit
