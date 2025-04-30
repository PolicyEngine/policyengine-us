from policyengine_us.model_api import *


class ca_capi(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "California CAPI"
    definition_period = YEAR
    defined_for = "ca_capi_eligible"
    reference = "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf"

    def formula(spm_unit, period, parameters):
        state_supplement_payment_standard = spm_unit(
            "ca_state_supplement", period
        )
        person = spm_unit.members
        ssi_amount_if_eligible = person("ssi_amount_if_eligible", period)
        eligible_person = person("ca_capi_eligible_person", period)
        total_ssi_amount = spm_unit.sum(
            ssi_amount_if_eligible * eligible_person
        )
        payment_standard = state_supplement_payment_standard + total_ssi_amount
        p = parameters(period).gov.states.ca.cdss.capi.payment_standard_offset
        married = spm_unit("spm_unit_is_married", period)
        offset = where(married, p.couple, p.single)
        total_payment_standard = max_(payment_standard - offset, 0)
        person = spm_unit.members
        countable_income = spm_unit.sum(
            (person("ssi_countable_income", period) * eligible_person)
        )
        return max_(0, total_payment_standard - countable_income)
