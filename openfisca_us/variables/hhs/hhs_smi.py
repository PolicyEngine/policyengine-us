from openfisca_core.model_api import *


class hhs_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = u"HHS SMI"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        household_size = spm_unit.household("household_size", period)
        state = spm_unit.household("state_code", period)
        four_person_smi = parameters(period).hhs.smi.amount[state]
        adjustment_mapping = parameters(
            period
        ).hhs.smi.household_size_adjustment
        first_person_rate = adjustment_mapping[first_person]
        second_to_sixth_additional_rate = adjustment_mapping[
            second_to_sixth_person
        ]
        seven_or_more_additional_rate = adjustment_mapping[additional_person]

        return where(
            household_size < 7,
            four_person_smi
            * (
                first_person_rate
                + second_to_sixth_additional_rate * (household_size - 1)
            ),
            four_person_smi
            * (
                first_person_rate
                + second_to_sixth_additional_rate * 5
                + seven_or_more_additional_rate * (household_size - 6)
            ),
        )
