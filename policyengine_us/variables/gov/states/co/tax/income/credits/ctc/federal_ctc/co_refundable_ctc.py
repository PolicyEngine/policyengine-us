from policyengine_us.model_api import *


class co_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Refundable Child Tax Credit replicated to include the Colorado limitations"
    unit = USD
    documentation = "Total value of the refundable portions of the Child Tax Credit."
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-129. Child tax credit - legislative declaration - definitions.
        "https://law.justia.com/codes/colorado/title-39/specific-taxes/income-tax/article-22/part-1/section-39-22-129/",
        # 2022 Colorado Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1",
        # Colorado Individual Income Tax Filing Guide - Instructions for Select Credits from the DR 0104CR - Line 1 Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16",
        # 1 CCR 201-2, Rule 39-22-129(1): the Colorado credit is a percentage
        # of the allowed federal child tax credit.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=1+CCR+201-2&ruleVersionId=10063#page=47",
        # No refundable federal CTC for filers electing a section 911 exclusion.
        "https://www.law.cornell.edu/uscode/text/26/24#d_3",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        # follow 2022 DR 0104CN form and its instructions (in Book cited above):
        adjusted_fed_ctc = tax_unit("co_non_refundable_ctc", period)  # Line 7
        max_child_amount = tax_unit("co_federal_ctc_maximum", period)  # Line 3
        credit_excess_over_tax = max_(0, max_child_amount - adjusted_fed_ctc)  # Line 8
        p = parameters(period).gov.irs.credits.ctc
        statutory_cap = p.refundable.individual_max  # Line 9
        children = tax_unit("co_ctc_eligible_children_count", period)
        total_statutory_cap = min_(
            statutory_cap * children, credit_excess_over_tax
        )  # Line 10
        earnings = tax_unit("tax_unit_earned_income", period)  # Line 11
        earnings_over_threshold = max_(
            0, earnings - p.refundable.phase_in.threshold
        )  # Line 12
        relevant_earnings = (
            earnings_over_threshold * p.refundable.phase_in.rate
        )  # Line 13
        social_security_tax = tax_unit(
            "ctc_social_security_tax", period
        )  # Line 14 - 16
        federal_eitc = tax_unit("eitc", period)  # Line 17a
        social_security_excess = max_(0, social_security_tax - federal_eitc)  # Line 18
        tax_increase = where(
            children < p.refundable.phase_in.min_children_for_ss_taxes_minus_eitc,
            relevant_earnings,
            max_(relevant_earnings, social_security_excess),
        )  # Line 19
        refundable_amount = min_(total_statutory_cap, tax_increase)  # Line 20
        # Colorado matches the allowed federal credit, so the federal section
        # 24(d)(3) bar on section 911 filers carries over.
        barred = tax_unit("refundable_ctc_barred_by_section_911_exclusion", period)
        return where(barred, 0, refundable_amount)
