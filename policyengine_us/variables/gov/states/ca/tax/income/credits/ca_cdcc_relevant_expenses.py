from policyengine_us.model_api import *


class ca_cdcc_relevant_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC-relevant care expenses replicated to include California limitations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-117-2-9631"
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
        # limit by the IRC § 129 employer-provided dependent care benefits
        # excluded from income (line 30 subtracts the excluded benefits, and
        # line 32 caps at the already-net federal Form 2441 line 31). Mirror the
        # § 21(c) reduction the federal credit's base applies.
        dollar_limit = cdcc.max * count_eligible
        exclusion = tax_unit("dependent_care_assistance_exclusion", period)
        dollar_limit_after_exclusion = max_(dollar_limit - exclusion, 0)
        eligible_capped_expenses = min_(expenses, dollar_limit_after_exclusion)
        # Then, cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
