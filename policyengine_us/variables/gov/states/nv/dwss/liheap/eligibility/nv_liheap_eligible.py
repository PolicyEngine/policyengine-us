from policyengine_us.model_api import *


class nv_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Nevada LIHEAP Fixed Annual Credit eligibility"
    defined_for = StateCode.NV
    reference = (
        "https://www.leg.state.nv.us/nrs/nrs-702.html#NRS702Sec260",
        # PDF pages 31, 34, 43, 60-61
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=31",
        # PDF pages 31, 34, 43, 60-61
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=31",
        # PDF pages 4-5, 8
        "https://liheapch.acf.gov/docs/2026/state-plans/NV_Plan_2026.pdf#page=4",
        # PDF pages 4-5, 8
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/fy-2027-low-income-home-energy-assistance-program-liheap-state-plan.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("nv_liheap_household_size", period)
        income = spm_unit("nv_liheap_countable_income", period)
        limit = spm_unit("nv_liheap_income_limit", period)
        # Countable annual gross income must not exceed the limit. No
        # household is categorically eligible and no asset test applies. The
        # 150% limit exceeds the 110% floor of 42 U.S.C. 8624(b)(2)(B) for
        # every size, so the floor never binds.
        income_eligible = income <= limit
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        # heating_type is a required input: any known fuel or NONE qualifies,
        # and an unspecified fuel qualifies only when heat is included in the
        # rent. Every household is assumed to have the active Nevada energy
        # account that Section 500 requires, so no heating bill, electricity
        # bill or cooling cost is needed. A credit on low or no energy costs
        # pays the minimum (Section 803 V).
        heating_type_reported = heat_in_rent | (
            heating_type != heating_type.possible_values.UNSPECIFIED
        )
        # Subsidized or public housing tenants whose utilities are all included
        # in the rent qualify only with an energy burden, a separately billed
        # energy cost (Sections 501 I, 503 and 803 V.3). Heat in the rent or a
        # tenant who does not pay utilities marks utilities in the rent; a home
        # without heating can only use the latter. The Section 42-only housing
        # exception, roomers and boarders, master meters and solar vendor
        # credits have no inputs.
        utilities_in_rent = heat_in_rent | ~spm_unit.household(
            "tenant_pays_utilities", period
        )
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        energy_burden = spm_unit("nv_liheap_energy_cost", period) > 0
        housing_eligible = ~(utilities_in_rent & subsidized) | energy_burden
        return (size > 0) & income_eligible & heating_type_reported & housing_eligible
