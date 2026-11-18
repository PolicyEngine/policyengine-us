from policyengine_us.model_api import *


class ca_dependent_care_assistance_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "California dependent care assistance exclusion"
    documentation = (
        "Employer-provided dependent care benefits excluded from gross income "
        "for California purposes, which reduce the California child and "
        "dependent care expenses credit's dollar limit (FTB 3506 Part IV)."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2017/17_3506.pdf#page=2",
        "https://www.ftb.ca.gov/forms/2021/2021-3506.pdf#page=2",
        "https://www.ftb.ca.gov/forms/2025/2025-3506.pdf#page=2",
        "https://www.ftb.ca.gov/forms/2021/2021-3506-instructions.html",
        # P.L. 117-2 section 9632 and P.L. 119-21 section 70404.
        "https://www.ftb.ca.gov/about-ftb/data-reports-plans/summary-of-federal-income-tax-changes/index.html#PL-117-2-9632",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        benefits = add(tax_unit, period, ["dependent_care_employer_benefits"])
        if not np.any(benefits > 0):
            return np.zeros_like(benefits)
        p = parameters(period).gov.states.ca.tax.income.credits.child_dependent_care
        # FTB 3506 Part IV lines 13-26 repeat Form 2441 Part III, except that
        # line 22 keeps California's own $5,000 ($2,500) cap: California did
        # not adopt the 2021 federal cap of $10,500 ($5,250).
        filing_status = tax_unit("filing_status", period)
        # A separate filer who is not considered married under IRC section
        # 21(e)(4) enters $5,000 (FTB 3506 instructions, line 20). For a
        # separate filer, cdcc_filing_status_eligible is that test.
        separate = filing_status == filing_status.possible_values.SEPARATE
        treated_as_unmarried = separate & tax_unit(
            "cdcc_filing_status_eligible", period
        )
        dollar_cap = where(
            treated_as_unmarried,
            p.dependent_care_assistance_cap["SINGLE"],
            p.dependent_care_assistance_cap[filing_status],
        )
        # FTB 3506 lines 17-18 limit benefits to independently known
        # qualified costs; lines 19-21 apply California earned income.
        # California taxes payroll HSA contributions, so its earnings may
        # exceed federal earnings, but never override the expense ceiling.
        qualified_expenses = where(
            tax_unit("count_cdcc_eligible", period) > 0,
            tax_unit("dependent_care_assistance_qualified_expenses", period),
            0,
        )
        earned_income_limit = tax_unit("ca_cdcc_min_head_spouse_earned", period)
        return max_(
            min_(
                benefits,
                min_(qualified_expenses, min_(dollar_cap, earned_income_limit)),
            ),
            0,
        )
