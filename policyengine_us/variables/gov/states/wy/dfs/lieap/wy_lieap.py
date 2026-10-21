from policyengine_us.model_api import *


class wy_lieap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Wyoming Low Income Energy Assistance Program benefit"
    documentation = (
        "Regular FY2026 heating assistance. SPM units approximate shared-heat "
        "households and report their own eligible seasonal primary heating cost. "
        "Approved income bands use inclusive upper bounds without ratio rounding; "
        "mixed-status households use qualified-member size, all otherwise countable "
        "income and no additional proration. Renters use the same schedule. "
        "Zero may indicate an unsupported fuel or missing eligible heating cost. "
        "Federal-floor households use the approved income-to-effective-limit "
        "ratio convention; their exact agency payment method is unverified. "
        "Years outside FY2026 are unverified estimates, including backfilled years."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/WY_BenefitMatrix_2026.xlsx",
        # Chapter 1, sections 10(d)-(e) and 13(b)(i), physical page 16.
        "https://rules.wyo.gov/Search.aspx?mode=7",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )
    defined_for = "wy_lieap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.lieap.payment
        income = max_(spm_unit("wy_lieap_countable_income", period), 0)
        limit = spm_unit("wy_lieap_income_limit", period)
        floor_rate = parameters(period).gov.hhs.liheap.fpg_floor
        guideline = spm_unit("wy_lieap_fpg", period).astype(np.float64)
        federal_floor = np.round(guideline * floor_rate, 2)
        limit = max_(limit, federal_floor)
        # Express each inclusive ceiling at the stored income precision.
        scale = p.entitlement_fraction
        ceilings = [
            (max_(limit, 1).astype(np.float64) * threshold).astype(income.dtype)
            for threshold in scale.thresholds[1:]
        ]
        fraction = select(
            [income <= ceiling for ceiling in ceilings],
            scale.amounts[:-1],
            default=scale.amounts[-1],
        )
        heating_type = spm_unit("heating_type", period)
        base = p.fuel_cost[heating_type] * fraction
        # The workbook rounds only the withheld amount, half-up to dollars.
        withheld = np.floor(base * p.holdback_rate + 0.5)
        expense = max_(spm_unit("heating_expense", period), 0)
        award = min_(base - withheld, expense)
        return where(award >= p.minimum_payment, award, 0)
