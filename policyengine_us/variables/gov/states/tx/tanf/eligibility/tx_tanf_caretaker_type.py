from policyengine_us.model_api import *


class TxTanfCaretakerType(Enum):
    NON_CARETAKER = "Non-caretaker"
    CARETAKER_WITHOUT_SECOND_PARENT = "Caretaker without second parent"
    CARETAKER_WITH_SECOND_PARENT = "Caretaker with second parent"


class tx_tanf_caretaker_type(Variable):
    value_type = Enum
    possible_values = TxTanfCaretakerType
    default_value = TxTanfCaretakerType.NON_CARETAKER
    entity = SPMUnit
    label = "Texas TANF caretaker type"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/c-110-tanf"
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_parent = person("is_parent", period)
        eligible_child = person("tx_tanf_eligible_child", period)

        # Count parents and eligible children
        parent_count = spm_unit.sum(is_parent)
        has_eligible_child = spm_unit.any(eligible_child)

        # Determine caretaker type based on parent count
        non_caretaker = ~has_eligible_child
        caretaker_without_second = has_eligible_child & (parent_count == 1)
        caretaker_with_second = has_eligible_child & (parent_count >= 2)

        return select(
            [non_caretaker, caretaker_without_second, caretaker_with_second],
            [
                TxTanfCaretakerType.NON_CARETAKER,
                TxTanfCaretakerType.CARETAKER_WITHOUT_SECOND_PARENT,
                TxTanfCaretakerType.CARETAKER_WITH_SECOND_PARENT,
            ],
            default=TxTanfCaretakerType.NON_CARETAKER,
        )
