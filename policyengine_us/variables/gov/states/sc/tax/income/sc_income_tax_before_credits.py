from policyengine_us.model_api import *


class sc_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina income tax before credits"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/forms-site/Forms/SC1040TT_2022.pdf"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("sc_taxable_income", period)
        p = parameters(period).gov.states.sc.tax.income.rates
        return p.calc(taxable_income)
