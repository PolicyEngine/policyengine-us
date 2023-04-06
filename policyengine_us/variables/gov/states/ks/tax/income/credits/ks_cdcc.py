from policyengine_us.model_api import *


class ks_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas child and dependent care expenses credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.credits
        return p.cdcc_fraction * tax_unit("cdcc", period)
