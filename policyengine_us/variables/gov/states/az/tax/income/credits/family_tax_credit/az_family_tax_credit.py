from policyengine_us.model_api import *


class az_family_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Family Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.family_tax_credits
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        amount = p.amount * tax_unit("tax_unit_size", period)
        eligible = tax_unit("az_family_tax_credit_eligible", period)
        return eligible * min_(amount, p.max_amount[filing_status])
