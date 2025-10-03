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
        # Caretaker type determines payment standard amount
        # Based on number of parents included in certified group

        person = spm_unit.members
        eligible_parent = person("tx_tanf_eligible_parent", period)
        eligible_child = person("tx_tanf_eligible_child", period)

        # Count payment-eligible parents and children
        parent_count = spm_unit.sum(eligible_parent)
        has_eligible_child = spm_unit.any(eligible_child)

        # Determine caretaker type
        # Non-caretaker: No parents in certified group (child-only cases)
        # Caretaker without second: One parent in certified group
        # Caretaker with second: Two or more parents in certified group
        non_caretaker = has_eligible_child & (parent_count == 0)
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
