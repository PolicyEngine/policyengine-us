from policyengine_us.model_api import *


class nyc_school_tax_credit_rate_reduction_amount_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for NYC School Tax Credit Rate Reduction Amount"
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # First get their NYC taxable income.
        nyc_taxable_income = tax_unit("nyc_taxable_income", period)

        # Then get the School Tax Credit rate reduction amount part of the parameter tree.
        p = parameters(
            period
        ).gov.local.ny.nyc.tax.income.credits.school.rate_reduction

        return nyc_taxable_income <= p.income_limit
