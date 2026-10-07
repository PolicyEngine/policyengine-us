from policyengine_us.model_api import *


class ctc_credit_limit_worksheet_b_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Schedule 8812 Credit Limit Worksheet B applies"
    documentation = (
        "Whether the filer completes Schedule 8812 Credit Limit Worksheet B, "
        "which lets the residential clean energy credit (and the adoption, "
        "mortgage interest and DC first-time homebuyer credits) displace the "
        "part of the Child Tax Credit that can be refunded. The IRS also "
        "requires the filer to claim one of those credits; that condition is "
        "omitted because Worksheet B changes nothing when those credits are "
        "zero."
    )
    definition_period = YEAR
    reference = (
        # 2025 Instructions for Schedule 8812, Credit Limit Worksheet A, line 3.
        "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4",
        "https://www.law.cornell.edu/uscode/text/26/24#d_1_B",
        # No refundable CTC for filers excluding foreign earned income under
        # section 911 (added as 24(d)(5), redesignated (d)(3) in 2018).
        "https://www.law.cornell.edu/uscode/text/26/24#d_3",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.ctc
        if p.refundable.fully_refundable:
            # In 2021, Worksheet B applied only to filers completing Part I-C,
            # whose CTC was not fully refundable.
            return np.zeros(tax_unit.count, dtype=bool)
        has_qualifying_child = tax_unit("ctc_qualifying_children", period) > 0
        # Form 2555 filers skip Worksheet B from 2015, when the refundable CTC
        # was first denied to them.
        files_form_2555 = tax_unit("foreign_earned_income_exclusion", period) > 0
        excluded = (
            files_form_2555 & p.refundable.foreign_earned_income_exclusion_bar_applies
        )
        return has_qualifying_child & ~excluded
