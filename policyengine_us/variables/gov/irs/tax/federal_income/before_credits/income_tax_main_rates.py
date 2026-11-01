from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.before_credits.tax_at_main_rates import (
    tax_at_main_rates,
)


class income_tax_main_rates(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax main rates"
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/1",
        "https://www.law.cornell.edu/uscode/text/26/911#f_1_A",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=37",
    ]
    unit = USD

    def formula(tax_unit, period, parameters):
        # compute taxable income that is taxed at the main rates; a taxpayer
        # excluding foreign earned income adds the excluded amount back
        # (Foreign Earned Income Tax Worksheet, line 3)
        full_taxable_income = tax_unit(
            "taxable_income_plus_section_911_exclusion", period
        )
        cg_exclusion = tax_unit("capital_gains_excluded_from_taxable_income", period)
        taxinc = max_(0, full_taxable_income - cg_exclusion)
        # compute tax using bracket rates and thresholds
        bracket = parameters(period).gov.irs.income.bracket
        filing_status = tax_unit("filing_status", period)
        tax = tax_at_main_rates(taxinc, filing_status, bracket)
        # 26 U.S.C. 911(f)(1)(A): less the tax on the excluded amount alone
        # (worksheet lines 5 and 6). The capital gain excess rule keeps the
        # excluded amount in the main-rates base, so the difference is never
        # negative here.
        excluded = max_(0, tax_unit("foreign_earned_income_exclusion", period))
        tax_on_excluded = tax_at_main_rates(excluded, filing_status, bracket)
        return where(excluded > 0, max_(0, tax - tax_on_excluded), tax)
