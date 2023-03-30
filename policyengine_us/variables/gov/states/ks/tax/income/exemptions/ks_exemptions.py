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
        num_exemptions = tax_unit("ks_count_exemptions", period)
        p = parameters(period).gov.states.ks.tax.income.exemptions
        return num_exemptions * p.amount
