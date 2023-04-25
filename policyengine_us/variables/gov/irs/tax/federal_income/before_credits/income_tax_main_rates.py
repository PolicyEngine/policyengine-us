from policyengine_us.model_api import *


class income_tax_main_rates(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax main rates"
    reference = "https://www.law.cornell.edu/uscode/text/26/1"
    unit = USD

    def formula(tax_unit, period, parameters):
        # compute taxable income that is taxed at the main rates
        full_taxable_income = tax_unit("taxable_income", period)
        cg_exclusion = tax_unit(
            "capital_gains_excluded_from_taxable_income", period
        )
        taxinc = max_(0, full_taxable_income - cg_exclusion)
        # compute tax using bracket rates and thresholds
        p = parameters(period).gov.irs.income
        bracket_tops = p.bracket.thresholds
        bracket_rates = p.bracket.rates
        filing_status = tax_unit("filing_status", period)
        tax = 0
        bracket_bottom = 0
        for i in range(1, len(list(bracket_rates.__iter__())) + 1):
            b = str(i)
            bracket_top = bracket_tops[b][filing_status]
            tax += bracket_rates[b] * amount_between(
                taxinc, bracket_bottom, bracket_top
            )
            bracket_bottom = bracket_top
        return tax
