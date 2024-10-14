from policyengine_us.model_api import *


class ks_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.exemptions
        if p.by_filing_status.in_effect:
            filing_status = tax_unit("filing_status", period)
            base_amount = p.by_filing_status.amount[filing_status]
            dependents = tax_unit("tax_unit_dependents", period)
            dependent_amount = p.by_filing_status.dependent * dependents
            return base_amount + dependent_amount
        exemptions_count = tax_unit("ks_count_exemptions", period)
        return exemptions_count * p.consolidated.amount
