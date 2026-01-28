from policyengine_us.model_api import *


class ca_child_care_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "California child care State Median Income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://www.cde.ca.gov/sp/cd/ci/mb2505.asp"

    def formula(spm_unit, period, parameters):
        # California uses July 1 fiscal year for SMI
        year = period.start.year
        month = period.start.month
        if month >= 7:
            instant_str = f"{year}-07-01"
        else:
            instant_str = f"{year - 1}-07-01"

        size = spm_unit("spm_unit_size", period.this_year)
        state_code = spm_unit.household("state_code_str", period.this_year)

        p = parameters(instant_str).gov.hhs.smi
        four_person_smi = p.amount[state_code]
        adjustment = p.household_size_adjustment
        threshold = p.additional_person_threshold
        size_adjustment = (
            adjustment.first_person
            + adjustment.second_to_sixth_person * (min_(size, threshold) - 1)
            + adjustment.additional_person * max_(size - threshold, 0)
        )
        return four_person_smi * size_adjustment / MONTHS_IN_YEAR
