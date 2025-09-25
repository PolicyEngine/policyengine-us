from policyengine_us.model_api import *


class pr_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico personal exemption"
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=2"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        # line 7
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.exemptions
        filing_status = tax_unit("filing_status", period)
        return p.personal[filing_status]
