from policyengine_us.model_api import *


class nj_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP medically necessary cooling eligibility"
    defined_for = StateCode.NJ
    reference = (
        # PDF pages 6, 13, 14.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=13",
        # PDF pages 6, 14, 15.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=14",
        # Section 3.1 (60% SMI) and section 3.3 (a doctor's note or a Utility
        # Critical Care Certification). PDF page 11.
        "https://liheapch.acf.gov/docs/2026/state-plans/NJ_Plan_2026.pdf#page=11",
        "https://liheapch.acf.gov/docs/2027/state-plans/NJ_Plan_2027.pdf#page=11",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-5-49-3-3",
    )
    documentation = (
        "Handbook 3.4 pays income-eligible households with medical evidence that a "
        "member's health will be seriously endangered unless the home is cooled. "
        "The benefit does not depend on the heating fuel or on a heating cost. The "
        "program is modeled from FY2022 (eligibility/in_effect). Payments of the "
        "cooling fuel by people outside the household and residence in a medical "
        "facility, community residence or treatment center deny the benefit but "
        "need inputs not available here."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.eligibility
        person = spm_unit.members
        # Handbook 3.4.A: medical evidence that the health of at least one
        # household member is endangered. Non-qualified noncitizens are left
        # out of the HEA household (handbook 2.2.5), so the member must count
        # toward nj_liheap_household_size.
        qualified = person("is_citizen_or_legal_immigrant", period)
        medical_need = spm_unit.any(
            qualified & person("has_medical_need_for_cooling", period)
        )
        # Handbook 3.4.A.2: the household pays the cooling fuel supplier, pays
        # fuel charges by usage, or pays cooling costs within a single rent
        # charge. has_cooling_expense is a cooling cost apart from rent, which
        # covers the first two routes. Cooling in the rent reads
        # tenant_pays_utilities, as other cooling programs do, because
        # heat_expense_included_in_rent covers heat only and heat in the rent
        # does not put the electric (cooling) bill there.
        utilities_in_rent = ~spm_unit.household("tenant_pays_utilities", period) & (
            add(spm_unit, period, ["rent"]) > 0
        )
        # Handbook 3.4.A.3.I: public housing or a rent subsidy that includes all
        # cooling costs is denied, since subsidized rent is not an out-of-pocket
        # cooling cost. A subsidized household with its own cooling bill stays
        # eligible.
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        responsible = spm_unit("has_cooling_expense", period) | (
            utilities_in_rent & ~subsidized
        )
        # Handbook 3.4.A.3.IV.
        dependent_students_only = spm_unit.all(
            person("is_full_time_student", period)
            & person("is_tax_unit_dependent", period)
        )
        size = spm_unit("nj_liheap_household_size", period)
        return (
            p.in_effect
            & medical_need
            & responsible
            & ~dependent_students_only
            & (size > 0)
            & spm_unit("nj_liheap_income_eligible", period)
        )
