from policyengine_us.model_api import *


class az_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Arizona Child Care Assistance Program copay"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/sites/default/files/dl/CCA-0229AFY26.pdf#page=1",
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=33",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.hhs.ccap.copay
        person = spm_unit.members
        fee_level = spm_unit("az_ccap_fee_level", period)
        eligible_child = person("az_ccap_eligible_child", period)
        attending_days = person("childcare_attending_days_per_month", period.this_year)
        per_child_copay = p.daily[fee_level] * attending_days * eligible_child
        return where(
            spm_unit("az_ccap_copay_exempt", period),
            0,
            spm_unit.sum(per_child_copay),
        )
