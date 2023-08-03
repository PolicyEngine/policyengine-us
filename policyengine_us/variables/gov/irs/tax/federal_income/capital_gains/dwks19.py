from policyengine_us.model_api import *


class dwks19(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS14"
    unit = USD
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )

    def formula(tax_unit, period, parameters):
        dwks14 = tax_unit("dwks14", period)
        capital_gains = parameters(period).gov.irs.capital_gains.brackets
        filing_status = tax_unit("filing_status", period)
        dwks1 = tax_unit("taxable_income", period)
        dwks16 = min_(capital_gains.thresholds["1"][filing_status], dwks1)
        dwks17 = min_(dwks14, dwks16)
        dwks10 = tax_unit("dwks10", period)
        dwks18 = max_(0, dwks1 - dwks10)
        return max_(dwks17, dwks18) * tax_unit("hasqdivltcg", period)
