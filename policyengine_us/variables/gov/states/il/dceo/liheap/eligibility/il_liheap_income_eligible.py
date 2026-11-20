from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class il_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Illinois LIHEAP income eligible"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://www.ilga.gov/documents/legislation/ilcs/documents/030500200K6.htm",
        "https://liheapch.acf.gov/docs/2027/state-plans/IL_Plan_2027.pdf#page=10",
        "https://ilvalley-edc.org/wp-content/uploads/2026/06/2027-LIHEAP-Benefit-Matrix-FINAL-20260616.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p_hhs = parameters(period).gov.hhs
        p_il = parameters(period).gov.states.il.dceo.liheap

        # Illinois uses 60% of state median income or 200% FPL, whichever is higher
        state_median_income = spm_unit("hhs_smi", period)
        smi_limit = state_median_income * p_hhs.liheap.smi_limit

        # Federal poverty guideline limit
        household_fpg = spm_unit("spm_unit_fpg", period)
        fpg_limit = household_fpg * p_il.eligibility.fpg_limit

        # Income concept - using IRS gross income as the base
        income = add(spm_unit, period, ["irs_gross_income"])

        # Eligible if income is below the higher of the two limits
        income_limit = max_(smi_limit, fpg_limit)

        if p_il.eligibility.provider_income_limits_in_effect:
            electricity = spm_unit("il_liheap_electricity_provider", period)
            gas = spm_unit("il_liheap_natural_gas_provider", period)
            electric_providers = electricity.possible_values
            gas_providers = gas.possible_values
            state_funded = (
                (electricity == electric_providers.AMEREN_ILLINOIS)
                | (electricity == electric_providers.COMED)
                | (gas == gas_providers.AMEREN_ILLINOIS)
                | (gas == gas_providers.NICOR_GAS)
                | (gas == gas_providers.NORTH_SHORE_GAS)
                | (gas == gas_providers.PEOPLES_GAS)
            )
            size = spm_unit("spm_unit_size", period)
            geography = spm_unit.household("state_group_str", period)
            guideline = fpg(
                size,
                geography,
                period,
                parameters,
                year_lag=p_il.eligibility.fpg_year_lag,
            )
            state_limit = guideline * p_il.eligibility.state_fpg_limit
            # Rounding the monthly SMI limit reproduces all twelve published
            # PY2027 monthly rows. This is reconciled from the table rather
            # than an express rounding instruction. The plan uses 150% FPG
            # instead of SMI above twelve members.
            federal_limit = where(
                size <= p_il.eligibility.smi_max_household_size,
                np.floor(smi_limit / MONTHS_IN_YEAR + 0.5) * MONTHS_IN_YEAR,
                guideline * p_hhs.liheap.fpg_limit,
            )
            income_limit = where(state_funded, state_limit, federal_limit)

        return income <= income_limit
