from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class in_eap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Indiana EAP household eligibility"
    defined_for = StateCode.IN
    reference = (
        # Section 3.1 (page 23), Section 4.4 (page 29), Section 8.3 (pages 69-70) and
        # Section 8.8 (pages 73-75).
        "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=23",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].ihcda.eap
        income = spm_unit("in_eap_income", period)
        limit = np.floor(spm_unit("in_eap_smi", period) * p.eligibility.income_limit)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 15 in PY2025 and size 16 in PY2026 and PY2027.
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("in_eap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            size, state_group, period, parameters, year_lag=p.eligibility.fpg_year_lag
        )
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        # Section 4.4 permits an ineligible adult to apply for eligible household members.
        # Emancipated minors, residency duration, eviction writs, SSNs, and sanctions
        # cannot be determined here. Section 8.8 separates household eligibility from
        # whether each utility can receive a benefit; burden is checked in in_eap.
        return (
            (add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0)
            & spm_unit.any(spm_unit.members("age", period) >= p.eligibility.adult_age)
            & ((income <= limit) | (income < floor))
        )
