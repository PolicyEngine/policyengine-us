from policyengine_us.model_api import *


class nc_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.nc.tax.income
        return p.deductions.standard.amount[filing_status]
