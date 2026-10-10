from policyengine_us.model_api import *


class ca_cdcc_relevant_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC-relevant care expenses replicated to include California limitations"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-117-2-9631",
        "https://www.ftb.ca.gov/forms/2021/2021-3506.pdf#page=2",
        "https://www.ftb.ca.gov/forms/2025/2025-3506.pdf#page=2",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        year = period.start.year
        if year == 2021:
            period_adjusted = f"{year - 1}-01-01"
        else:
            period_adjusted = f"{year}-01-01"

        # Qualifying expenses cover childcare plus care for a disabled
        # qualifying individual of any age (FTB 3506 instructions,
        # Section D).
        childcare = tax_unit("tax_unit_childcare_expenses", period)
        adult_care = add(tax_unit, period, ["care_expenses"])
        expenses = childcare + adult_care
        # First, cap based on the number of eligible care receivers
        cdcc = parameters(period_adjusted).gov.irs.credits.cdcc
        count_eligible = min_(
            cdcc.eligibility.max, tax_unit("count_cdcc_eligible", period)
        )
        # FTB 3506 Part IV (lines 26-33) reduces the $3,000 / $6,000 dollar
        # limit by California's excluded dependent care benefits. Line 22
        # keeps the $5,000 / $2,500 cap when the federal cap increases.
        dollar_limit = cdcc.max * count_eligible
        exclusion = tax_unit("ca_dependent_care_assistance_exclusion", period)
        dollar_limit_after_exclusion = max_(dollar_limit - exclusion, 0)
        # Lines 32-33 also cap the California base at federal Form 2441,
        # Part III, line 31. A larger federal exclusion can exhaust the
        # federal limit while California's own remaining limit is positive.
        federal_limit = tax_unit("cdcc_limit", period)
        eligible_capped_expenses = min_(
            expenses, min_(dollar_limit_after_exclusion, federal_limit)
        )
        # Then, cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
