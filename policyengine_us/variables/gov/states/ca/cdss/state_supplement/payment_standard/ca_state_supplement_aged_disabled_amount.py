from policyengine_us.model_api import *


class ca_state_supplement_aged_disabled_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement aged disabled amount"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_state_supplement_aged_disabled_count"
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.state_supplement.payment_standard.aged_or_disabled.amount
        # Aged or disabled amount
        aged_disabled_count = spm_unit(
            "ca_state_supplement_aged_disabled_count", period
        )
        return where(aged_disabled_count > 1, p.married, p.single)
