from numpy import ceil
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
        if cdcc.refundable or cdcc.abolition:
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


class c33200(Variable):
    value_type = float
    entity = TaxUnit
    label = "Credit for child and dependent care expenses"
    unit = USD
    documentation = "From form 2441, before refundability checks"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.cdcc
        max_credit = min_(tax_unit("f2441", period), 2) * cdcc.max
        c32800 = max_(0, min_(tax_unit("filer_e32800", period), max_credit))
        mars = tax_unit("mars", period)
        is_head = tax_unit.members("is_tax_unit_head", period)
        earnings = tax_unit.members("earned", period)
        is_spouse = tax_unit.members("is_tax_unit_spouse", period)
        lowest_earnings = where(
            mars == mars.possible_values.JOINT,
            min_(
                tax_unit.sum(is_head * earnings),
                tax_unit.sum(is_spouse * earnings),
            ),
            tax_unit.sum(is_head * earnings),
        )
        c33000 = max_(0, min_(c32800, lowest_earnings))
        c00100 = tax_unit("c00100", period)
        tratio = 0.01 * max_(
            ((c00100 - cdcc.phaseout.start) * cdcc.phaseout.rate), 0
        )
        exact = tax_unit("exact", period)
        crate = where(
            exact,
            max_(
                cdcc.phaseout.min,
                cdcc.phaseout.max
                - min_(
                    cdcc.phaseout.max - cdcc.phaseout.min,
                    tratio,
                ),
            ),
            max_(
                cdcc.phaseout.min,
                cdcc.phaseout.max - tratio,
            ),
        )
        tratio2 = max_(
            ((c00100 - cdcc.phaseout.second_start) * cdcc.phaseout.rate / 1e2),
            0,
        )
        crate_if_over_second_threshold = where(
            exact,
            max_(0, cdcc.phaseout.min - min_(cdcc.phaseout.min, tratio2)),
            max_(0, cdcc.phaseout.min - tratio),
        )
        crate = where(
            c00100 > cdcc.phaseout.second_start,
            crate_if_over_second_threshold,
            crate,
        )

        return c33000 * crate


class cdcc_refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Child/dependent care refundable credit"
    unit = USD
    documentation = "Refundable credit for child and dependent care expenses from Form 2441"

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.cdcc
        if cdcc.refundable and not cdcc.abolition:
            return tax_unit("c33200", period)
        else:
            return 0
