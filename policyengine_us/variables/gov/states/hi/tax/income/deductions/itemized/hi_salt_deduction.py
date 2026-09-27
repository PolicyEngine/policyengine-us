from policyengine_us.model_api import *


class hi_salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii state and local tax deduction"
    unit = USD
    reference = (
        "https://data.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0002_0004.htm",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=34",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        filing_status = tax_unit("filing_status", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        eligible = federal_agi < p.salt_income_limit[filing_status]
        income_or_sales_tax = tax_unit("state_and_local_sales_or_income_tax", period)
        deductible_tax = eligible * income_or_sales_tax
        if not p.salt_income_limit_applies_to_sales_tax:
            # Before 2019, sales taxes remain deductible above the income limit.
            sales_tax = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
            deductible_tax = max_(deductible_tax, sales_tax)
        # The income limit does not apply to real estate taxes.
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])
        return deductible_tax + real_estate_tax
