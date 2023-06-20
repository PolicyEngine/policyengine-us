from policyengine_us.model_api import *


class az_dependent_credit_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona dependent care credit amount"
    unit = USD
    documentation = "https://azdor.gov/file/12346/download?token=7FAdFbnT"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.credits.dependent_credit
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        dependent_amount = p.amount.calc(age) * dependent
        return tax_unit.sum(dependent_amount)
