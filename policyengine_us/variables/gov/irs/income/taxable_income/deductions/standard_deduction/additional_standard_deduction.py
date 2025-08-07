from policyengine_us.model_api import *


class additional_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Additional standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/63#f"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.standard
        filing_status = tax_unit("filing_status", period)
        amount_per = p.aged_or_blind.amount[filing_status]
        return amount_per * tax_unit("aged_blind_count", period)
