from openfisca_us.model_api import *
import numpy as np


class md_non_refundable_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CDCC"
    documentation = (
        "Maryland Child and Dependent Care Credit - Nonrefundable component"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.md.tax.income.credits.cdcc
        max_cdcc = tax_unit("md_max_cdcc", period)
        # Phases out based on filing status.
        phase_out_start = p.phase_out.start[filing_status]
        excess = max_(0, agi - phase_out_start)
        phase_out_increment = p.phase_out.increment[filing_status]
        phase_out_increments = np.ceil(excess / phase_out_increment)
        percent_reduction = phase_out_increments * p.phase_out.percent
        return max_(0, max_cdcc * (1 - percent_reduction))
