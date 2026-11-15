from policyengine_us.model_api import *


class ct_social_security_benefit_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut social security benefit adjustment"
    documentation = (
        "Form CT-1040 line 41, Conn. Gen. Stat. 12-701(a)(20)(B)(x). "
        "Following IRC 86(d)(1), the worksheet counts title II benefits and "
        "tier 1 railroad retirement benefits (the social security equivalent "
        "benefit) together. Clause (iv) subtracts the taxable tier 1 benefits "
        "that clause (x) does not, and the model subtracts them with the rest "
        "of the railroad annuity (taxable_railroad_benefits, 45 U.S.C. "
        "231m(a)), so this adjustment covers the title II benefits alone."
    )
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701",
        # Line 43: tier 1 and tier 2 benefits not already subtracted on
        # line 41.
        "https://portal.ct.gov/-/media/drs/forms/2024/income/2024-ct-1040-instructions_1224.pdf#page=9",
        # Social Security Benefit Adjustment Worksheet, lines A to F.
        "https://portal.ct.gov/-/media/drs/forms/2024/income/2024-ct-1040-instructions_1224.pdf#page=24",
    )
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ct.tax.income.subtractions.social_security

        # Line A: federal Social Security Benefits Worksheet line 1, the
        # head's and spouse's title II and tier 1 benefits (box 5 of Forms
        # SSA-1099 and RRB-1099).
        section_86_benefits = tax_unit("tax_unit_section_86_benefits", period)

        # Line B: federal worksheet line 9, the excess in IRC 86(b)(1).
        ss_combined_income_excess = tax_unit(
            "tax_unit_ss_combined_income_excess", period
        )

        # Lines C and D: 25% of the lesser of lines A and B.
        capped_benefits = min_(section_86_benefits, ss_combined_income_excess)
        capped_benefits_portion = capped_benefits * p.rate

        # Line E: federal worksheet line 18. The title II share stays here;
        # the tier 1 share goes to clause (iv).
        taxable_title_ii = tax_unit("tax_unit_taxable_social_security", period)

        # Line F, with line D taken from the title II benefits first, so
        # that clause (iv) subtracts every taxable tier 1 dollar.
        reduced_taxable_title_ii = max_(
            taxable_title_ii - capped_benefits_portion,
            0,
        )

        # Clause (x)(III): below the threshold, filers subtract all their
        # taxable benefits.
        agi = tax_unit("adjusted_gross_income", period)
        full_adjustment_eligible = agi < p.reduction_threshold[filing_status]

        return where(
            full_adjustment_eligible,
            taxable_title_ii,
            reduced_taxable_title_ii,
        )
