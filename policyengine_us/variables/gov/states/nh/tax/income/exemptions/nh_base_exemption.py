from policyengine_us.model_api import *


class nh_base_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire base exemption household level"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        individual_income = person("dividend_income", period) + person(
            "interest_income", period
        )
        amount = parameters(
            period
        ).gov.states.nh.tax.income.exemptions.amount.base
        base = min_(individual_income, amount)
        return tax_unit.sum(base)
