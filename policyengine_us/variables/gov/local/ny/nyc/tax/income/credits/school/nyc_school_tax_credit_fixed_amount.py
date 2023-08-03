from policyengine_us.model_api import *


class nyc_school_tax_credit_fixed_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC School Tax Credit Fixed Amount"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # First get their NYAGI.
        income = tax_unit("nyc_school_credit_income", period)

        # Then get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the School Tax Credit fixed amount part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.school.fixed

        # Calculate eligibility.
        eligible = income <= p.income_limit

        # Calculate amount if eligible, which varies only with filing status.
        amount_if_eligible = p.amount[filing_status]

        # Return calculated amount.
        return eligible * amount_if_eligible
