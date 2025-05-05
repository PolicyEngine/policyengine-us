from policyengine_us.model_api import *


class ca_state_supplement(Variable):
    value_type = float
    entity = SPMUnit
    label = "California state supplement"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit(
            "ca_state_supplement_payment_standard", period
        )
        ssi = add(spm_unit, period, ["ssi"])
        countable_income = add(spm_unit, period, ["ssi_countable_income"])
        return max_(0, payment_standard - ssi - countable_income)
