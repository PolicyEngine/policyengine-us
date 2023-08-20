from policyengine_us.model_api import *


class md_senior_tax_income_threshold(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Senior Tax Credit Income Threshold"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=15"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        
        p = parameters(period).gov.states["md"].tax.income.credits.senior_tax

        filing_status = tax_unit("filing_status", period)

        agi = tax_unit("adjusted_gross_income", period)
        return agi < p.income_threshold[filing_status]
