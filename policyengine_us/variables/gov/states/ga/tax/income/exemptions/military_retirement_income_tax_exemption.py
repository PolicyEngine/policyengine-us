from policyengine_us.model_api import *

class ga_military_retirement_income_tax_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia military retirement income tax exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        #income = tax_unit("ga_taxable_income", period)
        p = parameters(period).gov.states.ga.tax.income.exemptions.military_retirement.amount.age_threshold
        return p
