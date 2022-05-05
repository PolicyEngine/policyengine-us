from openfisca_us.model_api import *


class cdcc_refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Child/dependent care refundable credit"
    unit = USD
    documentation = "Refundable credit for child and dependent care expenses from Form 2441"
    reference = "https://www.law.cornell.edu/uscode/text/26/21#g_1"

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.cdcc
        if cdcc.refundable and not cdcc.abolition:
            return tax_unit("c33200", period)
        else:
            return 0
