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
        "Each printed Table 1 row starts at its listed ratio, so a ratio exactly "
        "at .21 takes the .21-.25 fraction and a ratio of 1.00 or more takes the "
        "1.00+ zero; a ratio between printed rows takes the earlier row, as if "
        "truncated to two decimals. Mixed-status households use qualified-member "
        "size, all otherwise countable income and no additional proration. "
        "Renters use the same schedule (rule 10(e)). The award is capped at a "
        "reported heating expense; a household whose heat is included in rent "
        "and reports no separate bill receives the standard formula for its "
        "fuel. Zero may indicate an unspecified fuel or missing heating "
        "responsibility. Federal-floor households take the fraction for their "
        "income relative to the raised limit, a modeling assumption; their exact "
        "agency payment method is unverified. Years outside FY2026 are "
        "unverified estimates, including backfilled years."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/WY_BenefitMatrix_2026.xlsx",
        # Rules 3(cc) and 3(kk).
        "https://www.law.cornell.edu/regulations/wyoming/agency-049/subagency-0024/chapter-1/049-1-Wyo-Code-R-SSSS-1-3",
        # Rule 8(b)(i)(B).
        "https://www.law.cornell.edu/regulations/wyoming/agency-049/subagency-0024/chapter-1/049-1-Wyo-Code-R-SSSS-1-8",
        # Rules 10(c)-(e).
        "https://www.law.cornell.edu/regulations/wyoming/agency-049/subagency-0024/chapter-1/049-1-Wyo-Code-R-SSSS-1-10",
        # Rule 13(b)(i).
        "https://www.law.cornell.edu/regulations/wyoming/agency-049/subagency-0024/chapter-1/049-1-Wyo-Code-R-SSSS-1-13",
        # FY2026 State Plan, section 2.3.
        "https://dfs.wyo.gov/wp-content/uploads/2025/10/FFY2026-LIEAP-State-Model-Plan.pdf#page=8",
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
        # Table 1 prints rows "0 - .20", ".21- .25", ... ".86 - .99" and
        # "1.00 +", so each listed ratio starts its row. Income below the
        # ceiling at a row's start stays in the preceding, higher-paying row.
        # The ceilings are kept at the precision of stored monetary inputs.
        scale = p.entitlement_fraction
        ceilings = [
            (max_(limit, 1).astype(np.float64) * threshold).astype(income.dtype)
            for threshold in scale.thresholds[1:]
        ]
        fraction = select(
            [income < ceiling for ceiling in ceilings],
            scale.amounts[:-1],
            default=scale.amounts[-1],
        )
        heating_type = spm_unit("heating_type", period)
        base = p.fuel_cost[heating_type] * fraction
        # The workbook rounds only the withheld amount, half-up to dollars.
        withheld = np.floor(base * p.holdback_rate + 0.5)
        adjusted_benefit = base - withheld
        # Rule 10(d) bars a computed benefit below the minimum before rule
        # 13(b)(i) limits payment to the actual primary fuel cost. Rule 10(e)
        # pays a renter whose heat is included in rent on the standard
        # formula, so the cost cap applies only when a heating bill is
        # reported.
        expense = spm_unit("heating_expense", period)
        payment = where(expense > 0, min_(adjusted_benefit, expense), adjusted_benefit)
        return where(adjusted_benefit >= p.minimum_payment, payment, 0)
