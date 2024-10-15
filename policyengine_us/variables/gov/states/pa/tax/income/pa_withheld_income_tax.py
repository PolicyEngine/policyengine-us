from policyengine_us.model_api import *


class pa_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania withheld income tax"
    defined_for = StateCode.PA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        # Pennsylvania does not have standard deductions, personal exemptions, or itemized deductions.
        # Also, They do not use the federal standard deduction amounts.
        p = parameters(period).gov.states.pa.tax.income
        return agi * p.rate
