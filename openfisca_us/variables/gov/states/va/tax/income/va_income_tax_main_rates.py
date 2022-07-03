from openfisca_us.model_api import *

class va_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia income tax before credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        va_income = parameters(period).gov.states.va.tax.income
        va_brackets = va_income.brackets
        va_agi = tax_unit('va_adjusted_gross_income', period)
        filing_status = tax_unit('filing_status', period)
        if va_agi < va_income.va_filing_thresholds[filing_status]:
            return 0
        va_taxable_income = tax_unit('va_taxable_income', period)

        reg_tax = 0
        last_reg_threshold = 0
        for i in range(1, 3):
            # Calculate the taxes owed on income up to current threshold
            reg_threshold = va_brackets.thresholds[str(i)]
            reg_tax += va_brackets.rates[str(i)] * amount_between(
                va_taxable_income, last_reg_threshold, reg_threshold
            )
            last_reg_threshold = reg_threshold

        # calculate tax on income above the last threshold
        reg_tax += va_brackets.rates["4"] * max_(va_taxable_income - last_reg_threshold, 0)

        return round_(reg_tax, 0)
