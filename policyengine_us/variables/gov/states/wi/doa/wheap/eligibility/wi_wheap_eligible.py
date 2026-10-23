from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class wi_wheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Wisconsin WHEAP regular heating benefit"
    defined_for = StateCode.WI
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/16/i/27",
        # Sections 3.2.1, 3.2.5, 3.3.1 and 4.4.28.3.
        # PDF pages 33, 41-43, 45-46, 87
        "https://web.archive.org/web/20260428215048/https://energyandhousing.wi.gov/Documents/WHEAP/WheapManual_PY26.pdf#page=33",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.doa.wheap.eligibility
        # A positive size means a citizen or eligible non-citizen can serve as
        # case head.
        size = spm_unit("wi_wheap_household_size", period)
        income = spm_unit("wi_wheap_countable_income", period)
        limit = spm_unit("wi_wheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below
        # 110% of the poverty guideline.
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        federal_floor = np.round(
            guideline * parameters(period).gov.hhs.liheap.fpg_floor, 2
        )
        categorical = spm_unit("wi_wheap_categorically_eligible", period)
        income_eligible = (income <= limit) | (income < federal_floor) | categorical
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        heating_reported = (heating_type != fuel.UNSPECIFIED) & (
            heating_type != fuel.NONE
        )
        # Heat included in rent is an energy burden unless the household
        # receives rental assistance or lives in public housing. Section 42
        # tax credit units keep the burden but are not distinguishable, and
        # shared-meter arrangements without payment are not identified.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        energy_burden = spm_unit("has_heating_expense", period) | (
            heat_in_rent & ~subsidized
        )
        # No asset test applies to regular benefits.
        return (size > 0) & income_eligible & heating_reported & energy_burden
