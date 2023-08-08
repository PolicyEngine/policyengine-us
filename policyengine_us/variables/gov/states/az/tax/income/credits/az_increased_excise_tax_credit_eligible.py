from policyengine_us.model_api import *


class az_increased_excise_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Eligible for Arizona Increased Excise Tax Credit"
    reference = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072-01.htm"
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.increased_excise
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        max_income = p.income_threshold[filing_status]
        return agi <= max_income
