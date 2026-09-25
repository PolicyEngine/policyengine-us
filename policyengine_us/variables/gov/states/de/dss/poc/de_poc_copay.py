from policyengine_us.model_api import *


class de_poc_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Delaware Purchase of Care family copayment"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = (
        "https://regulations.delaware.gov/AdminCode/title16/Department%20of%20Health%20and%20Social%20Services/Division%20of%20Social%20Services/11004.shtml",
        "https://dhss.delaware.gov/dss/childcr/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dss.poc.copay
        countable_income = spm_unit("de_poc_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(fpg > 0, countable_income / fpg, 0)
        return where(fpl_ratio <= p.waiver_fpl_rate, 0, countable_income * p.rate)
