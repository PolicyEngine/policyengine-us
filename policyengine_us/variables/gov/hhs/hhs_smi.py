from policyengine_us.model_api import *


def smi(unit_size, state, period, parameters):
    p = parameters(period).gov.hhs.smi
    size_threshold = p.additional_person_threshold
    capped_size = clip(unit_size - 1, 0, size_threshold - 1)
    extra_persons = max_(unit_size - size_threshold, 0)
    size_adjustment = (
        p.household_size_adjustment.first_person
        + p.household_size_adjustment.second_to_sixth_person * capped_size
        + p.household_size_adjustment.additional_person * extra_persons
    )
    return p.amount[state] * size_adjustment


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
        return smi(size, state, period, parameters)
