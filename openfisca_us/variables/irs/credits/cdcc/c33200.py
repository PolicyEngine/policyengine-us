from openfisca_us.model_api import *


class c33200(Variable):
    value_type = float
    entity = TaxUnit
    label = "Credit for child and dependent care expenses"
    unit = USD
    documentation = "From form 2441, before refundability checks"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.cdcc
        eligible_deps = min_(tax_unit("f2441", period), cdcc.eligibility.max)
        max_credit = eligible_deps * cdcc.max
        c32800 = max_(0, min_(tax_unit("filer_e32800", period), max_credit))
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        earnings = person("earned", period)
        is_spouse = person("is_tax_unit_spouse", period)
        head_earnings = tax_unit.sum(is_head * earnings)
        spouse_earnings = tax_unit.sum(is_spouse * earnings)
        lowest_earnings = where(
            filing_status == filing_status.possible_values.JOINT,
            min_(head_earnings, spouse_earnings),
            head_earnings,
        )
        c33000 = max_(0, min_(c32800, lowest_earnings))
        c00100 = tax_unit("c00100", period)
        tratio = 0.01 * max_(
            ((c00100 - cdcc.phaseout.start) * cdcc.phaseout.rate), 0
        )
        crate = max_(
            cdcc.phaseout.min,
            cdcc.phaseout.max
            - min_(
                cdcc.phaseout.max - cdcc.phaseout.min,
                tratio,
            ),
        )
        tratio2 = max_(
            ((c00100 - cdcc.phaseout.second_start) * cdcc.phaseout.rate / 1e2),
            0,
        )
        crate_if_over_second_threshold = max_(
            0, cdcc.phaseout.min - min_(cdcc.phaseout.min, tratio2)
        )
        crate = where(
            c00100 > cdcc.phaseout.second_start,
            crate_if_over_second_threshold,
            crate,
        )

        return c33000 * crate
