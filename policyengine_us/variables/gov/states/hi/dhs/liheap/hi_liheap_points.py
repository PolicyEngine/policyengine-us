from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class hi_liheap_points(Variable):
    value_type = int
    entity = SPMUnit
    label = "Hawaii LIHEAP private dwelling points before eligibility"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=10",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/HI_BenefitMatrix_2026.pdf#page=2,3",
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/07/Policies-and-Procedures-2020.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.liheap
        size = spm_unit("hi_liheap_household_size", period)
        income = spm_unit("hi_liheap_countable_income", period)
        group = spm_unit.household("state_group_str", period)
        poverty = fpg(
            max_(size, 1),
            group,
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        income_points = p.payment.points.income.calc(
            income.astype(np.float64) / poverty, right=True
        )
        size_points = p.payment.points.household_size.calc(size)
        county = spm_unit.household("county_str", period)
        # County identifies Oahu without another island input. The shared
        # county variable uses its existing first-county fallback if not supplied.
        # Explicitly unknown or out-of-state counties earn no regional points.
        oahu = county == "HONOLULU_COUNTY_HI"
        neighbor = np.isin(
            county,
            [
                "HAWAII_COUNTY_HI",
                "MAUI_COUNTY_HI",
                "KAUAI_COUNTY_HI",
                "KALAWAO_COUNTY_HI",
            ],
        )
        region = p.payment.points.region
        region_points = where(oahu, region.oahu, where(neighbor, region.neighbor, 0))
        person = spm_unit.members
        age = person("age", period)
        qualified = person("is_citizen_or_legal_immigrant", period)
        ages = p.payment.points.vulnerability
        vulnerable = spm_unit.any(
            qualified
            & (
                (age <= ages.child_max_age)
                | (age >= ages.elderly_min_age)
                | (person("is_disabled", period) & (age >= ages.adult_min_age))
            )
        )
        # The manual and gas application use ELECTRIC costs for burden even
        # when the requested credit pays gas. Annual costs approximate the
        # current paid bill. Positive costs with zero income have high burden;
        # zero costs and zero income do not establish an energy burden.
        electricity = spm_unit("pre_subsidy_electricity_expense", period)
        high_burden = (electricity > 0) & (
            electricity >= income * p.payment.points.burden_rate
        )
        points = income_points + size_points + region_points + vulnerable + high_burden
        # These are schedule points, not a dollar award or eligibility decision.
        return where(size > 0, points, 0)
