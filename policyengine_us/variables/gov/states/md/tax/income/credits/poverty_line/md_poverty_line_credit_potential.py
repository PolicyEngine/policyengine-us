from policyengine_us.model_api import *


class md_poverty_line_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Poverty Line Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-709&enactments=false",
        "https://www.law.cornell.edu/uscode/text/26/32#c_2",
        "https://www.law.cornell.edu/cfr/text/26/1.32-2",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-107&enactments=false",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2024/Resident-Booklet.pdf#page=22",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Earlier portions of the law define eligibility.
        eligible = tax_unit("is_eligible_md_poverty_line_credit", period)
        # (c)    Except as provided in subsection (e) of this section, the
        # credit allowed against the State income tax under subsection (b)(1)
        # of this section equals the lesser of:
        # (1) the State income tax determined after subtracting the credit
        # allowed under § 10–704(b)(1) of this subtitle; or
        income_tax_before_credits = tax_unit("md_income_tax_before_credits", period)
        md_married_or_has_child_non_refundable_eitc = tax_unit(
            "md_married_or_has_child_non_refundable_eitc", period
        )
        tax_after_non_refundable_eitc = (
            income_tax_before_credits - md_married_or_has_child_non_refundable_eitc
        )
        # (2)    an amount equal to 5% of the eligible low income taxpayer’s
        # earned income, as defined under § 32(c)(2) of the Internal Revenue
        # Code.
        # § 32(c)(2) earned income "is reduced by any net loss in earnings
        # from self-employment" (26 CFR 1.32-2(c)(2)), so it can be zero or
        # less. eitc_earned_income floors it at zero: a credit the taxpayer
        # "may claim" under § 10-709(b) cannot go negative and raise tax.
        # Form 502 Worksheet 18B line 2 instead leaves losses out ("Do not
        # include a farm or business loss."); this follows the statute's
        # § 32(c)(2) reference, which § 10-107 reads with federal
        # interpretations.
        p = parameters(period).gov.states.md.tax.income.credits.poverty_line
        earnings = tax_unit("eitc_earned_income", period)
        earnings_portion = earnings * p.earned_income_share
        amount_if_eligible = min_(tax_after_non_refundable_eitc, earnings_portion)
        return amount_if_eligible * eligible
