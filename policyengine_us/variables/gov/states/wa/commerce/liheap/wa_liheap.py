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
        "The approved model caps the minimum/maximum-adjusted award at "
        "reported heating cost and applies no extra mixed-status proration. "
        "No rent-included or missing-bill cost is imputed. Zero for missing cost "
        "or a household larger than the published adjuster table means an "
        "unsupported amount, not necessarily legal ineligibility. The SPM unit "
        "and its reported cost approximate the shared-heat household and cost. "
        "Years outside FY2026 are unverified estimates."
    )
    reference = (
        # Physical pages 1-2, printed worksheet pages 10-11.
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/WA_BenefitMatrix_2026.pdf#page=1",
        # Section 2.6, physical page 10.
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
        monthly_income = income.astype(np.float64) / MONTHS_IN_YEAR
        increment = p.intermediate_rounding_increment
        adjusted_income = (
            np.floor(monthly_income / max_(adjuster, 1) / increment + 0.5) * increment
        )
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
        # Approved ordering: minimum/maximum first, actual heating cost last.
        award = min_(clip(rounded_award, p.minimum, p.maximum), expense)
        return where(supported_size & (denominator > 0), award, 0)
