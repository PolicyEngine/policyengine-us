from policyengine_us.model_api import *


class co_ccap_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "State median income for Colorado CCAP"
    unit = USD
    documentation = "The state median income used to determine eligibility for Colorado's Child Care Assistance Program. This differs from the HHS definition by basing it on the prior year if before October, and dividing by 12."
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        state_code = spm_unit.household("state_code_str", period.this_year)
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        four_person_smi = parameters(instant_str).gov.hhs.smi.amount[
            state_code
        ]
        adjustment_mapping = parameters(
            instant_str
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
        return four_person_smi * size_adjustment / MONTHS_IN_YEAR
