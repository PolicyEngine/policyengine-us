from policyengine_us.model_api import *


class ct_pension_annuity_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut pension and annuity subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = "ct_pension_annuity_subtraction_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        rate = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.pensions_or_annuity.rate
        head_or_spouse = head | spouse
        pension_income = person("taxable_pension_income", period)
        eligible_pension = pension_income * head_or_spouse
        total_pension = tax_unit.sum(eligible_pension)
        return total_pension * rate
