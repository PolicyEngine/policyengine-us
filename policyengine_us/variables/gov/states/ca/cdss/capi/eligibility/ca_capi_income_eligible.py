from policyengine_us.model_api import *


class ca_capi_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CAPI income eligible"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf"

    def formula(spm_unit, period, parameters):
        payment_standard = add(
            spm_unit,
            period,
            ["ssi_amount_if_eligible", "ca_state_supplement_payment_standard"],
        )
        person = spm_unit.members
        eligible_person = person("ca_capi_eligible_person", period)
        countable_income = spm_unit.sum(
            (person("ssi_countable_income", period) * eligible_person)
        )
        return payment_standard > countable_income
