from policyengine_us.model_api import *


def smi_size_factor(unit_size, period, parameters):
    """Return the 45 CFR 96.85(b) share of the four-person SMI for a size."""
    p = parameters(period).gov.hhs.smi
    size_threshold = p.additional_person_threshold
    capped_size = clip(unit_size - 1, 0, size_threshold - 1)
    extra_persons = max_(unit_size - size_threshold, 0)
    return (
        p.household_size_adjustment.first_person
        + p.household_size_adjustment.second_to_sixth_person * capped_size
        + p.household_size_adjustment.additional_person * extra_persons
    )


def smi(unit_size, state, period, parameters):
    p = parameters(period).gov.hhs.smi
    return p.amount[state] * smi_size_factor(unit_size, period, parameters)


def liheap_smi_limit(unit_size, state, rate, period, parameters):
    """Return the LIHEAP limit at a rate of the size-adjusted SMI.

    HHS multiplies the rate times the four-person SMI by the size factor
    (LIHEAP IM 2025-02, Attachment 4). Flooring the four-person amount, then
    the size-adjusted amount, reproduces the published tables; HHS does not
    state a rounding order. Pass an earlier date as the period to use a prior
    year's SMI.
    """
    four_person_smi = parameters(period).gov.hhs.smi.amount[state]
    four_person_limit = np.floor(four_person_smi * rate)
    size_factor = smi_size_factor(unit_size, period, parameters)
    return np.floor(four_person_limit * size_factor)


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
