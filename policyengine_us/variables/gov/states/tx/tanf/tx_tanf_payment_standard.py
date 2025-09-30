from policyengine_us.model_api import *


class tx_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/c-110-tanf"
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Payment standard (maximum benefit amount) varies by household size and caretaker type

        size = spm_unit("tx_tanf_assistance_unit_size", period)
        caretaker_type = spm_unit("tx_tanf_caretaker_type", period)
        p = parameters(period).gov.states.tx.tanf.payment_standard

        # Determine caretaker type
        non_caretaker = (
            caretaker_type == caretaker_type.possible_values.NON_CARETAKER
        )
        caretaker_without_second = (
            caretaker_type
            == caretaker_type.possible_values.CARETAKER_WITHOUT_SECOND_PARENT
        )
        caretaker_with_second = (
            caretaker_type
            == caretaker_type.possible_values.CARETAKER_WITH_SECOND_PARENT
        )

        # Select payment standard based on caretaker type
        return select(
            [non_caretaker, caretaker_without_second, caretaker_with_second],
            [
                p.non_caretaker.calc(size),
                p.caretaker_without_second_parent.calc(size),
                p.caretaker_with_second_parent.calc(size),
            ],
            default=0,
        )
