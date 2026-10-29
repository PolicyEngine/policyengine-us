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
        "household applies to the heating fuel or electric bill it picks for "
        "heating or cooling: energy burden, propane, income and vulnerable "
        "population points times the point value. Heating and cooling share "
        "this one annual benefit. Verified for FY2026 and FY2027; earlier "
        "years are unverified estimates through parameter backfilling. Crisis "
        "assistance and weatherization are out of scope."
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
        # PDF pages 2-3
        "https://www.hca.nm.gov/wp-content/uploads/LHP-602-English-LIHEAP-Application-05.01.2026.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.liheap
        income = spm_unit("nm_liheap_countable_income", period)
        heating_bill = spm_unit("heating_expense", period)
        electric_bill = spm_unit("pre_subsidy_electricity_expense", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # The annual bill over 12 months, floored at the energy standard
        # allowance, stands in for the highest monthly bill of the last 12
        # months, and annual income over 12 months for 30-day income. The
        # ratio of the annual amounts equals the monthly bill over monthly
        # income. It is computed in float64 with a single division per bill,
        # so a burden exactly at a cutoff lands on it even when the monthly
        # amounts have no exact binary value.
        allowance = p.payment.energy_standard_allowance * MONTHS_IN_YEAR
        income_64 = income.astype(np.float64)
        has_income = income > 0
        burden_points = p.payment.energy_burden_points

        def bill_points(bill):
            burden = np.divide(
                max_(bill.astype(np.float64), allowance),
                income_64,
                out=np.zeros_like(income_64),
                where=has_income,
            )
            # Households with zero income receive the top energy burden
            # points. Without a direct bill there are no energy points.
            points = where(
                has_income, burden_points.calc(burden), burden_points.amounts[-1]
            )
            return where(bill > 0, points, 0)

        # The household picks one heating or cooling bill, modeled as the one
        # giving more points: the heating fuel bill, with the propane points
        # when that fuel is propane, or the electric bill. Households whose
        # utilities are all included in the rent have no direct bill, and
        # households that heat with wood they do not purchase receive no
        # energy points.
        propane = heating_type == types.PROPANE
        heating_points = bill_points(heating_bill) + where(
            propane & (heating_bill > 0), p.payment.propane_points, 0
        )
        electric_points = bill_points(electric_bill)
        unpurchased_wood = (heating_type == types.WOOD) & (heating_bill == 0)
        energy_cost_points = where(
            unpurchased_wood, 0, max_(heating_points, electric_points)
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
        # Three income points at or below the low-income cutoff, a share of
        # the guideline (see low_income_fpg_rate), and two points above it.
        # Annual income against the annual cutoff equals the monthly test.
        income_points = where(
            income <= guideline * p_income.low_income_fpg_rate,
            p_income.low,
            p_income.high,
        )
        # Each vulnerable group with at least one counted member adds points
        # once. A member receiving disability-based income (Social Security
        # disability benefits, employment disability benefits, or SSI paid on
        # the basis of blindness or disability, not age) qualifies, and
        # is_disabled stands in for a doctor's statement. SSI is
        # MONTH-defined, so add() sums it over the year.
        person = spm_unit.members
        age = person("age", period)
        counted = person("is_citizen_or_legal_immigrant", period)
        young_child = spm_unit.any(counted & (age < p.payment.young_child_max_age + 1))
        elderly = spm_unit.any(counted & (age >= p.payment.elderly_age))
        ssi_recipient = (add(person, period, ["ssi"]) > 0) | (
            add(person, period, ["receives_ssi"]) > 0
        )
        ssi_disability = ssi_recipient & (
            person("is_blind", period) | person("is_ssi_disabled", period)
        )
        disability_income = (
            add(person, period, ["social_security_disability", "disability_benefits"])
            > 0
        ) | ssi_disability
        disabled = spm_unit.any(
            counted & (person("is_disabled", period) | disability_income)
        )
        vulnerable_groups = (
            young_child.astype(int) + elderly.astype(int) + disabled.astype(int)
        )
        vulnerable_points = vulnerable_groups * p.payment.vulnerable_points
        points = energy_cost_points + income_points + vulnerable_points
        # One benefit per federal fiscal year, with no bill cap. Supplemental
        # benefits at the secretary's direction are not modeled.
        return points * p.payment.point_value
