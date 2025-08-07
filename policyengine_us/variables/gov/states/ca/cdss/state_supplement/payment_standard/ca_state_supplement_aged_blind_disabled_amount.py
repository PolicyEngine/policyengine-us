from policyengine_us.model_api import *


class ca_state_supplement_aged_blind_disabled_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement aged disabled and blind amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        blind_amount = spm_unit("ca_state_supplement_blind_amount", period)
        aged_disabled_amount = spm_unit(
            "ca_state_supplement_aged_disabled_amount", period
        )
        return max_(blind_amount, aged_disabled_amount)
