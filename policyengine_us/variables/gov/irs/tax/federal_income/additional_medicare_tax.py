from policyengine_us.model_api import *


class additional_medicare_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Additional Medicare Tax"
    unit = USD
    documentation = (
        "Additional Medicare Tax from Form 8959 (included in payrolltax)"
    )

    def formula(tax_unit, period, parameters):
        amc = parameters(period).gov.irs.payroll.medicare.additional
        # Wage and self-employment income are taxed the same.
        ELEMENTS = ["employment_income", "taxable_self_employment_income"]
        wages_plus_se = add(tax_unit, period, ELEMENTS)
        exclusion = amc.exclusion[tax_unit("filing_status", period)]
        base = max_(0, wages_plus_se - exclusion)
        return amc.rate * base
