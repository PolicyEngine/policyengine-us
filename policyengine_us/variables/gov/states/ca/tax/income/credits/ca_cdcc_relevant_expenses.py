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
            period_adjusted = f"{year-1}-01-01"
        else:
            period_adjusted = f"{year}-01-01"

        # First, cap based on the number of eligible care receivers
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        cdcc = parameters(period_adjusted).gov.irs.credits.cdcc
        count_eligible = min_(
            cdcc.eligibility.max, tax_unit("count_cdcc_eligible", period)
        )
        eligible_capped_expenses = min_(expenses, cdcc.max * count_eligible)
        # Then, cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
