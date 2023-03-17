from policyengine_us.model_api import *


class ks_fstc(Variable):
    value_type = float
    entity = TaxUnit
    label = "KS food sales tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    """
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.credits
    """
