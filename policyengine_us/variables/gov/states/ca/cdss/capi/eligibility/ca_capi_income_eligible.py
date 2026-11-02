from policyengine_us.model_api import *


class ca_capi_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CAPI income eligible"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=25"
    )

    def formula(spm_unit, period, parameters):
        # MPP 49-035.1 compares each individual's or couple's countable income
        # with the CAPI payment standard; a payment remains only when it is lower.
        return add(spm_unit, period, ["ca_capi_person"]) > 0
