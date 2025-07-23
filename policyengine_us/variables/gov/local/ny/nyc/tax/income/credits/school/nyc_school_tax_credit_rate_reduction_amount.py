from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value


class nyc_school_tax_credit_rate_reduction_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC School Tax Credit Rate Reduction Amount"
    unit = USD
    definition_period = YEAR
    defined_for = "nyc_school_tax_credit_rate_reduction_amount_eligible"

    def formula(tax_unit, period, parameters):
        # First get their NYC taxable income.
        nyc_taxable_income = tax_unit("nyc_taxable_income", period)

        # Then get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the School Tax Credit rate reduction amount part of the parameter tree.
        p = parameters(
            period
        ).gov.local.ny.nyc.tax.income.credits.school.rate_reduction

        # Calculate amount if eligible, which varies only with filing status.
        return select_filing_status_value(
            filing_status,
            p.amount,
            nyc_taxable_income,
        )
