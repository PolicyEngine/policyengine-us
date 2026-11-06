from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ga_caps_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia CAPS based on income"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=49",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixA-CAPS%20Maximum%20Income%20Limits%20by%20Family%20Size.pdf#page=1",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=52",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.income.smi_rate
        # Appendix A takes up the state median income table each October (October
        # 5 in 2026), so read the table at the month. hhs_smi keeps one table
        # through the calendar year. The chart prints annual limits rounded up to
        # the next dollar, and Manual 8.8.4 multiplies monthly income by 12 to
        # compare with it. Round to cents first so floating-point noise can't push
        # a whole-dollar limit up by one or move a family at the limit.
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, period, parameters)
        enrolled = spm_unit("ga_caps_enrolled", period)
        rate = where(enrolled, p.ongoing_eligibility, p.initial_eligibility)
        income_limit = np.ceil(np.round(annual_smi * rate, 2))
        annual_income = np.round(
            spm_unit("ga_caps_countable_income", period) * MONTHS_IN_YEAR, 2
        )
        # CAPS/00-7, 7.5: foster parents of children in DFCS custody need not meet
        # the income requirement. The family fee applies the same family-wide test.
        has_dfcs_custody_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        return (annual_income <= income_limit) | has_dfcs_custody_child
