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
        # The credit match is limited to the amount of CDCC claimed
        # we will represent this by capping the CDCC at federal income tax
        # before non-refundable credits
        cdcc = tax_unit("cdcc", period)
        income_tax_before_credits = tax_unit(
            "income_tax_before_credits", period
        )
        capped_cdcc = min_(cdcc, income_tax_before_credits)
        return p.cdcc_fraction * capped_cdcc
