from policyengine_us.model_api import *


class la_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Louisiana LIHEAP regular heating assistance"
    documentation = (
        "Louisiana's single regular heating-season award from the FFY2026 "
        "Heating and Cooling Benefit Matrix: an amount by energy burden, on a "
        "total-energy-cost basis, and household size, plus one priority group "
        "supplement, whose disability group also covers Social Security "
        "disability benefits and SSI paid on the basis of disability. Verified "
        "for FY2026; earlier and later years are unverified estimates through "
        "parameter backfilling. Louisiana also pays a separate summer cooling "
        "award from the same matrix, with 45.5% of FY2026 funds against 25% for "
        "heating, so program-year regular assistance can be twice this amount; "
        "the cooling award, crisis assistance and weatherization are out of "
        "scope."
    )
    defined_for = "la_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/LA_BenefitMatrix_Heat-Cool_2026.pdf",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20REVISED%20January%201_%202024.pdf#page=41",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=48",
        "https://liheapch.acf.gov/docs/2026/state-plans/LA_Plan_2026.pdf#page=10",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.lhc.liheap
        income = spm_unit("la_liheap_countable_income", period)
        # NOTE: the formula also runs for ineligible units, whose energy cost can
        # be negative; the floor keeps their burden band inside the matrix.
        energy_cost = max_(spm_unit("la_liheap_energy_cost", period), 0)
        # Annual cost over annual income stands in for the application-month
        # bill over 30-day income. Heat included in unsubsidized rent counts
        # only separately billed energy, so its band is a lower bound.
        has_income = income > 0
        burden = np.divide(
            energy_cost,
            income,
            out=np.zeros_like(energy_cost),
            where=has_income,
        )
        burden_band = p.payment.burden_band
        # Households with zero income receive the maximum benefit for their
        # size, the top burden band.
        band = where(has_income, burden_band.calc(burden), burden_band.amounts[-1])
        size = spm_unit("la_liheap_household_size", period)
        size_group = p.payment.size_group.calc(size)
        base = p.payment.amount[band][size_group]
        person = spm_unit.members
        age = person("age", period)
        # Section 4.2 A accepts proof of disability from the Social Security
        # Administration, so Social Security disability benefits and SSI paid on
        # the basis of disability also place a member in the group.
        receives_ssi = (add(person, period, ["ssi"]) > 0) | (
            add(person, period, ["receives_ssi"]) > 0
        )
        disabled = (
            person("is_disabled", period)
            | (person("social_security_disability", period) > 0)
            | (receives_ssi & person("is_ssi_disabled", period))
        )
        priority_group = (
            (age >= p.elderly_age)
            | disabled
            | (age < p.payment.young_child_max_age + 1)
        )
        priority_member = person("is_citizen_or_legal_immigrant", period) & (
            priority_group
        )
        supplement = spm_unit.any(priority_member) * p.payment.priority_supplement
        # One award covers the heating season, with no bill cap. Supplemental
        # heating payments depend on available funds and are not modeled.
        return base + supplement
