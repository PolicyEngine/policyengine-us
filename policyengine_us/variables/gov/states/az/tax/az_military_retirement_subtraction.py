from policyengine_us.model_api import *


class az_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Military Retirement Subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income
        #
        military_retirement_pay = tax_unit(
        head = person("is_tax_unit_spouse",
        spouse - same 
        head_or_spouse = head | spouse
        military_retirement_pay = person(
            "military_retirement_pay", period
        )
        eligible_military_pay = military_retirement_pay * head_or_spouse 
        return min_(tax_unit.sum(eligible_military_pay), p.military_retirement_subtraction)
