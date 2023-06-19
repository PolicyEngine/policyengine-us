from policyengine_us.model_api import *


class ga_low_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "georgia low income credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        
        num_exemptions = tax_unit("ga_count_exemptions", period)
        p = parameters(period).gov.states.ga.tax.income.credits.low_income_credit
        return num_exemptions * p.amount
        
    