from policyengine_us.model_api import *


class salt_cap(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT cap"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        filing_status = tax_unit("filing_status", period)
        return p.cap[filing_status]
