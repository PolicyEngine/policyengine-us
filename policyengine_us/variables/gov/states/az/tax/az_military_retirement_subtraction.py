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
        military_retirement_pay = tax_unit(
            "military_retirement_pay", period
        )
        return min_(military_retirement_pay, p.military_retirement_subtraction)
