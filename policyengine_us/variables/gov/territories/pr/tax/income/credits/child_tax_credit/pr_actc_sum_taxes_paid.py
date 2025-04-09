from policyengine_us.model_api import *


class pr_actc_sum_taxes_paid(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico additional child tax credit taxes paid"
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040ss.pdf#page=2"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.actc
        # check me: self-employment is person level
        # line 12a-c
        taxes_to_be_halved = add(tax_unit, period, ["self_employment_tax", "additional_medicare_tax"])  
        # lines 13a-f
        withheld_tax = tax_unit("pr_withheld_income", period)  
        
        # line 14
        return (taxes_to_be_halved * p.fraction) + withheld_tax  