from policyengine_us.model_api import *


class wa_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Washington Low Income Home Energy Assistance Program benefit"
    documentation = (
        "FY2026 regular heating award using reported annual heating expense. "
        "The printed worksheet supplies constants and household adjusters; "
        "two-decimal intermediate rounding, half-up ties and final dollar "
        "rounding are documented conventions consistent with its example. "
        "The award after the minimum and maximum is capped at reported "
        "heating cost, with no extra mixed-status proration. A household "
        "whose heat is included in rent, with a known fuel and no reported "
        "cost, receives the plan's minimum benefit without the cost cap as a "
        "lower bound, because the surrogate heat-cost schedule is not "
        "published; a reported cost keeps the worksheet calculation. An "
        "unspecified fuel pays zero, so callers must send heating_type. Zero "
        "for a household larger than the published adjuster table means an "
        "unsupported amount, not necessarily legal ineligibility. The SPM unit "
        "and its reported cost approximate the shared-heat household and cost. "
        "Years outside FY2026 are unverified estimates."
    )
    reference = (
        # PDF pages 1-2 (printed worksheet pages 10-11).
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/WA_BenefitMatrix_2026.pdf#page=1",
        # Sections 2.6 and 9.1, PDF pages 10,24.
        "https://liheapch.acf.gov/docs/2026/state-plans/WA_Plan_2026.pdf#page=10",
    )
    defined_for = "wa_liheap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.commerce.liheap.payment
        size = spm_unit("wa_liheap_household_size", period)
        adjuster = p.household_adjuster.calc(size)
        # Do not extrapolate the worksheet beyond its last published size.
        supported_size = size <= p.household_adjuster.thresholds[-1]
        income = max_(spm_unit("wa_liheap_countable_income", period), 0)
        increment = p.intermediate_rounding_increment
        annual_increment = MONTHS_IN_YEAR * max_(adjuster, 1) * increment
        lower_units = np.floor(income.astype(np.float64) / annual_increment)
        # Compare half-cent ties at the precision of the stored annual income.
        midpoint = ((lower_units + 0.5) * annual_increment).astype(income.dtype)
        adjusted_income = (lower_units + (income >= midpoint)) * increment
        denominator = p.income_constant - adjusted_income
        # Defensive handling for unsupported future-year extrapolations.
        quotient = np.divide(
            p.quotient_numerator,
            denominator,
            out=np.zeros_like(denominator),
            where=denominator > 0,
        )
        quotient = np.floor(quotient / increment + 0.5) * increment
        multiplier = max_(p.multiplier_constant - quotient, 0)
        expense = max_(spm_unit("heating_expense", period), 0)
        rounded_award = np.floor(expense * multiplier + 0.5)
        # Apply the minimum and maximum first, then cap at actual heating cost.
        cost_award = min_(clip(rounded_award, p.minimum, p.maximum), expense)
        # Plan section 2.6 sets a $250 minimum benefit, and section 9.1 pays
        # households whose heat is included in rent by check. The surrogate
        # heat-cost schedule is not published, so a known-fuel household with
        # heat in rent and no reported cost receives the minimum as a lower
        # bound, with no cost cap. An unspecified fuel pays zero.
        heating_type = spm_unit("heating_type", period)
        known_fuel = heating_type != heating_type.possible_values.UNSPECIFIED
        unpriced_heat_in_rent = (
            spm_unit("heat_expense_included_in_rent", period)
            & (expense <= 0)
            & known_fuel
        )
        award = where(unpriced_heat_in_rent, p.minimum, cost_award)
        return where(supported_size & (denominator > 0), award, 0)
