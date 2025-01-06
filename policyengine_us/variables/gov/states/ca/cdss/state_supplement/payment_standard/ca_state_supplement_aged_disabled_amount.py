from policyengine_us.model_api import *


class ca_state_supplement_aged_disabled_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement aged disabled amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.state_supplement.payment_standard
        # Blind amount
        is_married = spm_unit("spm_unit_is_married", period)

        # Aged or disabled amount
        aged_disabled_count = spm_unit(
            "ca_state_supplement_aged_disabled_count", period
        )
        return select(
            [
                (aged_disabled_count >= 2) & (is_married == 1),
                aged_disabled_count == 1,
            ],
            [
                p.aged_or_disabled.amount.married,
                p.aged_or_disabled.amount.single,
            ],
            default=0,
        )
