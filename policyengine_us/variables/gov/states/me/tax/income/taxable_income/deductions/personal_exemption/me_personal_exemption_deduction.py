from policyengine_us.model_api import *


class me_personal_exemption_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine personal exemption deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # P.L. 2017, c. 474, Part B, sections 6 and 7.
        "https://www.mainelegislature.org/legis/bills/bills_128th/chapters/"
        "PUBLIC474.asp",
        "https://www.govinfo.gov/content/pkg/USCODE-2017-title26/html/"
        "USCODE-2017-title26-subtitleA-chap1-subchapB-partV-sec151.htm",
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5126-A.html",
        # Form 1040ME instructions, line 13: a filer who may be claimed as a
        # dependent has no exemption; on a joint return each spouse is
        # counted separately.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_gen_instr_w_cover_pg.pdf#page=5",
    )
    defined_for = StateCode.ME

    def formula_2015(tax_unit, period, parameters):
        return tax_unit("exemptions", period)

    def formula_2018(tax_unit, period, parameters):
        # First get their Maine AGI.
        me_agi = tax_unit("me_agi", period)

        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the Maine Personal Credit part of the parameter tree.
        p = parameters(period).gov.states.me.tax.income.deductions.personal_exemption

        # Calculate the Personal Exemption phase-out parameters based on
        # filing status.
        phaseout_start = p.phaseout.start[filing_status]
        excess = max_(me_agi - phaseout_start, 0)  # Line 3
        phaseout_width = p.phaseout.width[filing_status]  # Line 4
        phaseout_percent = min_(1, excess / phaseout_width)  # Line 5

        # Get their Maine personal exemptions (line 6, from Form 1040ME line
        # 13). A filer who may be claimed as a dependent on another person's
        # return gets no exemption: a joint return counts 1 when only one
        # spouse may be claimed and 0 when both may.
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        exemptions = where(
            dependent_filer,
            tax_unit("head_spouse_count_not_dependent_elsewhere", period),
            tax_unit("head_spouse_count", period),
        )
        max_amount = exemptions * p.amount

        # Calculate the phaseout amount (line 7).
        phaseout_amount = phaseout_percent * max_amount

        return max_amount - phaseout_amount  # Line 8
