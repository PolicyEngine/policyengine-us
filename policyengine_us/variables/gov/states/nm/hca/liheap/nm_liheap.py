from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nm_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Mexico LIHEAP regular heating assistance"
    documentation = (
        "New Mexico's one regular benefit per federal fiscal year, which the "
        "household applies to heating or cooling: energy burden, propane, "
        "income and vulnerable population points times the point value. "
        "Heating and cooling share this one annual benefit. Verified for "
        "FY2026 and FY2027; earlier years are unverified estimates through "
        "parameter backfilling. Crisis assistance and weatherization are out "
        "of scope."
    )
    defined_for = "nm_liheap_eligible"
    reference = (
        # 8.150.620.8 through 8.150.620.10 NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0620.html",
        # 8.150.110.8 D NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0110.html",
        "https://www.hca.nm.gov/wp-content/uploads/Heating-and-Cooling-Point-and-Income-Guide-2026.pdf",
        "https://www.hca.nm.gov/wp-content/uploads/NM-LIHEAP-FFY-2027-Point-and-Income-Guidelines.pdf",
        # PDF pages 9-10
        "https://liheapch.acf.gov/docs/2026/state-plans/NM_Plan_2026.pdf#page=9",
        "https://www.hca.nm.gov/wp-content/uploads/DETAILED-MODEL-PLAN-LIHEAP_10_01_2026-4.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.liheap
        income = spm_unit("nm_liheap_countable_income", period)
        heating_expense = spm_unit("heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # Households whose utilities are included in the rent and households
        # that heat with wood they do not purchase receive no energy burden
        # points.
        unpurchased_wood = (heating_type == types.WOOD) & (heating_expense == 0)
        receives_energy_points = ~heat_in_rent & ~unpurchased_wood
        # The annual heating bill over 12 months, floored at the energy
        # standard allowance, stands in for the highest monthly bill of the
        # last 12 months, and annual income over 12 months for 30-day income.
        # The ratio of the annual amounts equals the monthly bill over monthly
        # income. It is computed in float64 with a single division, so a
        # burden exactly at a cutoff lands on it even when the monthly
        # amounts have no exact binary value.
        annual_bill = max_(
            heating_expense.astype(np.float64),
            p.payment.energy_standard_allowance * MONTHS_IN_YEAR,
        )
        income_64 = income.astype(np.float64)
        has_income = income > 0
        burden = np.divide(
            annual_bill,
            income_64,
            out=np.zeros_like(income_64),
            where=has_income,
        )
        burden_points = p.payment.energy_burden_points
        # Households with zero income receive the top energy burden points.
        energy_points = where(
            has_income, burden_points.calc(burden), burden_points.amounts[-1]
        )
        propane = heating_type == types.PROPANE
        energy_cost_points = receives_energy_points * (
            energy_points + propane * p.payment.propane_points
        )
        p_income = p.payment.income_points
        size = spm_unit("nm_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            size,
            state_group,
            period,
            parameters,
            year_lag=p.eligibility.fpg_year_lag,
        )
        # Three income points at or below the low-income cutoff, 110% of the
        # guideline (see low_income_fpg_rate), and two points above it. The
        # rate is applied to the guideline for each household size and the
        # monthly cutoff is rounded to the nearest dollar, which reproduces
        # the guides' printed rows for sizes 1-8. For sizes 9 and over, the
        # guides' "each additional" increments can differ by $1 or more a
        # month, growing with size (FFY2027 size 9: $5,629 by increment,
        # $5,628 by rate).
        monthly_cutoff = np.floor(
            guideline * p_income.low_income_fpg_rate / MONTHS_IN_YEAR + 0.5
        )
        monthly_income = income / MONTHS_IN_YEAR
        income_points = where(
            monthly_income <= monthly_cutoff, p_income.low, p_income.high
        )
        # Each vulnerable group with at least one counted member adds points
        # once. is_disabled stands in for disability-based income or a
        # doctor's statement.
        person = spm_unit.members
        age = person("age", period)
        counted = person("is_citizen_or_legal_immigrant", period)
        young_child = spm_unit.any(counted & (age < p.payment.young_child_max_age + 1))
        elderly = spm_unit.any(counted & (age >= p.payment.elderly_age))
        disabled = spm_unit.any(counted & person("is_disabled", period))
        vulnerable_groups = (
            young_child.astype(int) + elderly.astype(int) + disabled.astype(int)
        )
        vulnerable_points = vulnerable_groups * p.payment.vulnerable_points
        points = energy_cost_points + income_points + vulnerable_points
        # One benefit per federal fiscal year, with no bill cap. Supplemental
        # benefits at the secretary's direction are not modeled.
        return points * p.payment.point_value
