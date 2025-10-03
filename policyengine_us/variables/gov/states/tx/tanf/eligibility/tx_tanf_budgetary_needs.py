from policyengine_us.model_api import *


class tx_tanf_budgetary_needs(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF budgetary needs amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/c-110-tanf",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-2",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Budgetary needs varies by caretaker type and household size
        size = spm_unit("tx_tanf_assistance_unit_size", period)
        caretaker_type = spm_unit("tx_tanf_caretaker_type", period)
        p = parameters(period).gov.states.tx.tanf.needs_standard

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

        # Select appropriate budgetary needs table
        return select(
            [non_caretaker, caretaker_without_second, caretaker_with_second],
            [
                p.budgetary_needs_non_caretaker.calc(size),
                p.budgetary_needs_caretaker_without_second_parent.calc(size),
                p.budgetary_needs_caretaker_with_second_parent.calc(size),
            ],
            default=0,
        )
