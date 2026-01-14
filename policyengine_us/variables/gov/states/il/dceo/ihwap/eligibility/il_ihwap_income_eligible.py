from policyengine_us.model_api import *


class il_ihwap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Illinois IHWAP income eligible"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/6862#7",
        "https://dceo.illinois.gov/communityservices/homeweatherization.html",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dceo.ihwap.eligibility
        fpg = spm_unit("spm_unit_fpg", period)
        income = add(spm_unit, period, ["irs_gross_income"])
        return income <= fpg * p.fpg_limit
