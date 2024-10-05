from policyengine_us.model_api import *


class ri_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island standard deduction"
    unit = USD
    documentation = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/ADV_2022_40_Inflation_Adjustments.pdf"
    definition_period = YEAR
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        percentage = tax_unit(
            "ri_standard_deduction_applicable_percentage", period
        )
        return p.amount[filing_status] * percentage
