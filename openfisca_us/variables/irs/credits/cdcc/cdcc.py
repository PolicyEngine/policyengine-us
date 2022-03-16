from openfisca_us.model_api import *


class c07180(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Child/dependent care credit"
    unit = USD
    documentation = "Nonrefundable credit for child and dependent care expenses from Form 2441"

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.cdcc
        if cdcc.refundable:
            return 0
        else:
            return min_(
                max_(
                    0,
                    tax_unit("c05800", period) - tax_unit("e07300", period),
                ),
                tax_unit("c33200", period),
            )


cdcc = variable_alias("cdcc", c07180)


class cdcc_refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Child/dependent care refundable credit"
    unit = USD
    documentation = "Refundable credit for child and dependent care expenses from Form 2441"

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.cdcc
        if cdcc.refundable:
            return tax_unit("c33200", period)
        else:
            return 0
