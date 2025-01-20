from policyengine_us.model_api import *


class salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT deduction"
    unit = USD
    documentation = "State and local taxes plus real estate tax deduction from taxable income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        salt_amount = add(
            tax_unit,
            period,
            p.sources,
        )
        cap = p.cap[tax_unit("filing_status", period)]
        return min_(cap, salt_amount)
