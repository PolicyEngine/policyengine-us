from policyengine_us.model_api import *


class income_tax_main_rates(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax main rates"
    reference = "https://www.law.cornell.edu/uscode/text/26/1"
    unit = USD

    def formula(tax_unit, period, parameters):
        # Define taxable income taxed at main (i.e., regular) rates
        full_taxable_income = tax_unit("taxable_income", period)
        cg_exclusion = tax_unit(
            "capital_gains_excluded_from_taxable_income", period
        )
        reg_taxinc = max_(0, full_taxable_income - cg_exclusion)

        # Initialise regular income tax to zero
        reg_tax = 0
        last_reg_threshold = 0
        individual_income = parameters(period).gov.irs.income
        filing_status = tax_unit("filing_status", period)
        for i in range(1, 7):
            # Calculate rate applied to regular income up to the current
            # threshold (on income above the last threshold)
            reg_threshold = individual_income.bracket.thresholds[str(i)][
                filing_status
            ]
            reg_tax += individual_income.bracket.rates[
                str(i)
            ] * amount_between(reg_taxinc, last_reg_threshold, reg_threshold)
            last_reg_threshold = reg_threshold

        # Calculate regular income tax above the last threshold
        reg_tax += individual_income.bracket.rates["7"] * max_(
            reg_taxinc - last_reg_threshold, 0
        )
        return reg_tax
