from policyengine_us.model_api import *


class mo_ptc_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri property tax credit gross income"
    documentation = (
        "Total household income on Form MO-PTS, Line 8: Missouri adjusted "
        "gross income increased by the items in RSMo 135.010(5)(a) to (e)."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://dor.mo.gov/forms/4711_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435&hl=property+tax+credit%u2044",
        # PDF pages 1-2: Lines 1 to 8.
        "https://dor.mo.gov/forms/MO-PTS_2025.pdf#page=1",
        # Instructions for Form MO-PTS, Lines 2 to 7.
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=18",
        # Part 1, Line 8 (exempt federal interest) and Line 10 (military
        # retirement benefits).
        "https://dor.mo.gov/forms/MO-A_2025.pdf#page=1",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # Line numbers in comments below refer to the 2025 Form MO-PTS.
        person = tax_unit.members
        p = parameters(period).gov.states.mo.tax.income
        # Income is the claimant's, and the spouse's on a combined return
        # (RSMo 135.010(1) and (5)). As in mo_adjusted_gross_income, a
        # dependent's items are on their own return; Form MO-PTS brings in
        # minor children's amounts only on Lines 2 and 6.
        not_dependent = ~person("is_tax_unit_dependent", period)
        missouri_agi = person("mo_adjusted_gross_income", period)  # Line 1
        # Line 3: pensions, annuities and interest not included in Missouri
        # AGI, under RSMo 135.010(5)(b) and (e), each in its total amount.
        # Candidate: us-mo:property-tax-credit-pension-excludable-cost until registered.
        line_3_sources = [
            "tax_exempt_pension_income",
            "tax_exempt_retirement_distributions",
            # Subtracted from Missouri AGI on Form MO-A, Part 1, Line 10.
            "military_retirement_pay",
            "tax_exempt_interest_income",
            # Subtracted from Missouri AGI on Form MO-A, Part 1, Line 8.
            "us_govt_interest_person",
        ]
        line_3_income = not_dependent * add(person, period, line_3_sources)
        core_income = tax_unit.sum(missouri_agi + line_3_income)
        # Line 2: Social Security benefits not included in Missouri AGI.
        exempt_socsec_benefits = tax_unit("tax_exempt_social_security", period)
        # Line 5: veterans payments and benefits. Under RSMo 135.010(5)(a)
        # they don't count when the claimant or the claimant's spouse is a
        # one hundred percent service-connected disabled veteran, and such a
        # veteran never lists their own. Social Security on Line 2 still
        # counts, as Form MO-PTS Lines 2 and 4 carry no such exception.
        # Candidate: us-mo:property-tax-credit-veteran-exception-scope until registered.
        veterans_benefits = person("veterans_benefits", period)
        fully_disabled_veteran = person(
            "is_fully_disabled_service_connected_veteran", period
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        claimant_is_veteran = tax_unit.any(fully_disabled_veteran & head_or_spouse)
        veterans_benefits_income = where(
            claimant_is_veteran,
            0,
            tax_unit.sum(~fully_disabled_veteran * veterans_benefits),
        )
        # Line 6: public assistance received in cash.
        p_ptc = p.credits.property_tax
        public_assistance_income = tax_unit.sum(
            add(person, period, p_ptc.public_assistance_types)
        )
        # Line 7: RSMo 135.010(5)(d) allows no deduction for losses not
        # incurred in a trade or business. Schedule C and Schedule F losses
        # are business losses and stay deducted; the net capital loss
        # deduction and the listed Schedule E losses are added back. As in
        # limited_business_loss, a dependent's losses are on their own return.
        own_losses = 0
        for source in p_ptc.nonbusiness_loss_sources:
            own_losses = own_losses + max_(0, -person(source, period))
        listed_losses = tax_unit.sum(not_dependent * own_losses)
        # Section 461(l) can leave part of the business, farm and Schedule E
        # losses undeducted. Only the deducted share lowered federal AGI.
        deducted = tax_unit("limited_business_loss", period)
        all_losses = deducted + tax_unit("excess_business_loss", period)
        deducted_share = np.ones_like(all_losses)
        mask = all_losses > 0
        deducted_share[mask] = deducted[mask] / all_losses[mask]
        nonbusiness_losses = (
            tax_unit("limited_capital_loss", period) + listed_losses * deducted_share
        )
        if p.federal_agi.negative_floor_applies:
            # A negative federal AGI enters Missouri AGI as zero, so the part
            # of the losses below zero never reduced Line 1. Add back only the
            # part that brought federal AGI down to zero.
            federal_agi = tax_unit("adjusted_gross_income", period)
            nonbusiness_losses = min_(
                nonbusiness_losses, max_(0, federal_agi + nonbusiness_losses)
            )
        return (  # Line 8
            core_income
            + exempt_socsec_benefits
            + veterans_benefits_income
            + public_assistance_income
            + nonbusiness_losses
        )
