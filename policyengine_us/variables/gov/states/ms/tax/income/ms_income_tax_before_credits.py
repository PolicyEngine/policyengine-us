from policyengine_us.model_api import *


class ms_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi income tax before credits filing seperately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        filing_separately = tax_unit("ms_files_separately", period)
        income_separate = add(tax_unit, period, ["ms_taxable_income_indiv"])
        income_joint = tax_unit("ms_taxable_income_joint", period)
        
        applicable_income = where(filing_separately, income_separate, income_joint)

        rate = parameters(period).gov.states.ms.tax.income.rate
        
        return rate.calc(applicable_income)
