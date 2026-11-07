from policyengine_core.periods import instant
from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ga_caps_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia CAPS based on income"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        # PDF pages 27, 49, 52
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=27",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixA-CAPS%20Maximum%20Income%20Limits%20by%20Family%20Size.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.income
        # Each Appendix A chart dates the state median income table it takes up,
        # which smi_year_lag carries. The chart prints annual limits rounded up to
        # the next dollar, and Manual 8.8.4 multiplies monthly income by 12 to
        # compare with it. Round to cents first so floating-point noise can't push
        # a whole-dollar limit up by one or move a family at the limit.
        size = spm_unit("ga_caps_family_size", period)
        state = spm_unit.household("state_code_str", period.this_year)
        table_date = instant(period).offset(-int(p.smi_year_lag), "year")
        annual_smi = smi(size, state, table_date, parameters)
        enrolled = spm_unit("ga_caps_enrolled", period)
        rate = where(
            enrolled, p.smi_rate.ongoing_eligibility, p.smi_rate.initial_eligibility
        )
        income_limit = np.ceil(np.round(annual_smi * rate, 2))
        annual_income = np.round(
            spm_unit("ga_caps_countable_income", period) * MONTHS_IN_YEAR, 2
        )
        return annual_income <= income_limit
