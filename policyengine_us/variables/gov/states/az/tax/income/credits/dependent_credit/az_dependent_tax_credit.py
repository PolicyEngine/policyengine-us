from policyengine_us.model_api import *


class az_dependent_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona dependent tax credit"
    unit = USD
    documentation = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01073-01.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.dependent_credit
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        dependent_amount = p.amount.calc(age) * dependent
        amount = tax_unit.sum(dependent_amount)
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        reduction_start = p.reduction.start[filing_status]
        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / p.reduction.increment)
        reduction_percentage = min_(increments * p.reduction.percentage, 1)
        return amount * (1 - reduction_percentage)
