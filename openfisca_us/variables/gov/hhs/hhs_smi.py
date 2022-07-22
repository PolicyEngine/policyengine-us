from openfisca_us.model_api import *


class hhs_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "State Median Income (HHS)"
    documentation = "SPM unit's median income as defined by the Department of Health and Human Services, based on their state and size"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period)
        state = spm_unit.household("state_code_str", period)
        four_person_smi = parameters(period).gov.hhs.smi.amount[state]
        adjustment_mapping = parameters(
            period
        ).gov.hhs.smi.household_size_adjustment
        first_person_rate = adjustment_mapping.first_person
        second_to_sixth_additional_rate = (
            adjustment_mapping.second_to_sixth_person
        )
        seven_or_more_additional_rate = adjustment_mapping.additional_person
        size_adjustment = (
            first_person_rate
            + second_to_sixth_additional_rate * (min_(size, 6) - 1)
            + seven_or_more_additional_rate * max_(size - 6, 0)
        )
        return four_person_smi * size_adjustment
