from policyengine_us.model_api import *


class nyc_school_tax_credit_fixed_amount_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for NYC School Tax Credit Fixed Amount"
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # Eligibility is based on having a federal AGI below $30k
        # and being an NYC full-time resident.

        # Get the NYC School Tax Credit Fixed Amount part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.school.fixed

        # Get income that counts towards the NYC School Tax Credit.
        nyc_stc_income = tax_unit("nyc_school_credit_income", period)

        return nyc_stc_income <= p.income_limit
