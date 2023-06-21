from policyengine_us.model_api import *


class nc_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions "
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nc.tax.income
        filing_status = tax_unit("filing_status", period)
        return p.deductions.standard.amount[filing_status]