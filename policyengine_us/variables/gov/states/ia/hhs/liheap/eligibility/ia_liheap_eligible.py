from policyengine_us.model_api import *


class ia_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Iowa LIHEAP Regular Assistance"
    documentation = (
        "Iowa household with at least one counted member, countable income at "
        "or below 200 percent of the federal poverty guidelines, an energy "
        "burden, and a known primary heating fuel. Section 5.30 requires "
        "applicants to be 'living in Iowa, in their primary residence'. Iowa has "
        "no categorical eligibility and no assets test. Application timing, "
        "first-come first-served funding, the once-per-program-year limit and "
        "the automatically eligible verification waiver are not modeled."
    )
    reference = (
        # Section 5.10 Eligibility Criteria and 5.30 Who Can Apply (page 18),
        # Section 5.50 Energy Burden (page 22), Section 7.30 (page 34) and
        # Appendix D (pages 122-123).
        "https://hhs.iowa.gov/media/17262/download?inline#page=18",
        # Sections 1.4-1.7 (no categorical eligibility) and 2.3 (no assets
        # test), pages 5 and 8.
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=8",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Section 7.30: "A household comprised entirely of ineligible members
        # is ineligible to receive LIHEAP."
        has_counted_member = spm_unit("ia_liheap_household_size", period) > 0
        income_eligible = spm_unit("ia_liheap_income_eligible", period)
        energy_burden = spm_unit("ia_liheap_has_energy_burden", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # UNSPECIFIED pays nothing under the all-state convention (callers must
        # send the fuel; the fuel row of the matrix cannot be scored without
        # it). NONE means the home has no heating. Appendix D: a household whose
        # heat "is obtained from solar cells, wind power, an extension cord, or
        # a generator" has no energy burden.
        fuel_known = (
            (heating_type != types.UNSPECIFIED)
            & (heating_type != types.NONE)
            & (heating_type != types.SOLAR)
        )
        return has_counted_member & income_eligible & energy_burden & fuel_known
