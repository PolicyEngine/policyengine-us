from policyengine_us.model_api import *


class ok_federal_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal Child Tax Credit allowed for Oklahoma child credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK
    reference = (
        # 68 O.S. Sec. 2357(B)(2) (Oklahoma Child Care/Child Tax Credit).
        "https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=92568",
        # 2025 Form 511 packet, pages 11 and 25.
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=11",
        # 2025 Instructions for Schedule 8812, Credit Limit Worksheet A.
        "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4",
        "https://www.law.cornell.edu/uscode/text/26/25D#c",
    )
    documentation = (
        "Federal Child Tax Credit allowed for Oklahoma's Child Care/Child "
        "Tax Credit, including both non-refundable CTC actually used against "
        "federal income tax and refundable additional CTC."
    )

    def formula(tax_unit, period, parameters):
        credits = parameters(period).gov.irs.credits
        non_refundable_credits = credits.non_refundable
        refundable_ctc = tax_unit("refundable_ctc", period)
        # NOTE: Fully-refundable-CTC reforms (e.g. the American Family Act
        # contrib) drop non_refundable_ctc from the federal list, so there is
        # no non-refundable portion and the whole CTC flows through refundable.
        # Under AFA the $500 ODC is split into a separate non_refundable
        # other_dependent_credit entry, so returning refundable_ctc here
        # deliberately excludes that applied ODC (a conservative counterfactual
        # choice); the baseline keeps the ODC inside ctc, so it is unaffected.
        if "non_refundable_ctc" not in non_refundable_credits:
            return refundable_ctc
        # The credits applied before the CTC are those Schedule 8812 Credit
        # Limit Worksheet A subtracts, not those listed before it in the
        # non-refundable list: line 2, and on line 4 the residential clean
        # energy credit only when Credit Limit Worksheet B applies. Otherwise
        # that credit follows the CTC (26 U.S.C. 25D(c)).
        limit = credits.ctc_tax_liability_limit

        def applied(credit_list):
            credit_list = [c for c in credit_list if c in non_refundable_credits]
            return add(tax_unit, period, credit_list) if credit_list else 0

        worksheet_b_applies = tax_unit("ctc_credit_limit_worksheet_b_applies", period)
        preceding_credits = applied(limit.preceding_credits) + where(
            worksheet_b_applies, applied(limit.subsequent_credits), 0
        )

        non_refundable_ctc = tax_unit("non_refundable_ctc", period)
        total_non_refundable_credits = tax_unit(
            "income_tax_non_refundable_credits", period
        )
        capped_non_refundable_credits = tax_unit(
            "income_tax_capped_non_refundable_credits", period
        )
        income_tax_cap_binds = (
            capped_non_refundable_credits < total_non_refundable_credits
        )
        applied_non_refundable_ctc = min_(
            non_refundable_ctc,
            max_(0, capped_non_refundable_credits - preceding_credits),
        )
        applied_non_refundable_ctc = where(
            income_tax_cap_binds,
            applied_non_refundable_ctc,
            non_refundable_ctc,
        )
        return applied_non_refundable_ctc + refundable_ctc
