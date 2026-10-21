from policyengine_us.model_api import *


class az_property_tax_credit_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona adjusted gross income for property tax credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Adjusted gross income as defined for Arizona property tax credit purposes, "
        "for members who are not dependents. Per ARS 43-1072(H)(6) and ITR 12-1, "
        "this starts with federal AGI and subtracts taxable Social Security (ARS "
        "43-1072(I)). Federal AGI already leaves out most other subsection (I) "
        "items, but it counts unemployment whichever state paid it, so Arizona "
        "unemployment is not removed. Unlike regular Arizona income tax, this does "
        "NOT exclude pension income, capital gains, or Arizona exemptions. "
        "Capital gains and losses are each member's Form 140PTC line D amount, with "
        "a net loss limited per member, in place of the capital gains and capital "
        "loss deduction that federal AGI holds. Dependents' income, including their "
        "line D amounts, is in az_property_tax_credit_dependent_income. Can be "
        "negative."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072
        "https://azdor.gov/sites/default/files/2023-03/RULINGS_INDV_2012_itr12-1.pdf",  # ITR 12-1
        "https://www.law.cornell.edu/regulations/arizona/Ariz-Admin-Code-SS-R15-2C-502",
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
    ]
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # Start with Federal AGI
        # Per ITR 12-1, income includes wages, interest, business/farm income,
        # rent/royalty, S-corp/partnership income, alimony, capital gains,
        # pension/annuity income, and other non-excluded income.
        federal_agi = tax_unit("adjusted_gross_income", period)

        # Per ARS 43-1072(I) and ITR 12-1 "Items Excluded from Income",
        # we ONLY exclude Social Security benefits (and other items like
        # railroad retirement, workers comp, AZ unemployment, veterans
        # disability pensions, welfare, and gifts - but these are typically
        # not in Federal AGI anyway).
        #
        # Federal AGI only includes the TAXABLE portion of Social Security,
        # but for property tax credit, ALL Social Security should be excluded.
        # So we subtract the taxable portion that's in Federal AGI.
        taxable_social_security = tax_unit("tax_unit_taxable_social_security", period)

        # NOTE: We do NOT subtract Arizona's regular subtractions here because:
        # - Pension exclusions (az_public_pension_exclusion,
        #   az_military_retirement_subtraction) should be INCLUDED per
        #   ITR 12-1 item (9)
        # - Capital gains subtraction (az_long_term_capital_gains_subtraction)
        #   should be INCLUDED per ITR 12-1 item (7)
        # - US Government interest should be INCLUDED per ITR 12-1 item (2)
        # - Arizona exemptions (aged, blind) should NOT be subtracted

        # Capital gains and losses (Form 140PTC Part 1 line D). A.A.C.
        # R15-2C-502(C)(3) and ITR 12-1 item (7) count each member's net
        # capital gain or loss, with a net loss limited to $1,500 for each
        # member. Federal AGI instead adds each non-dependent's positive
        # capital gains (irs_gross_income) and, within loss_ald, deducts the
        # return's capital losses up to its gains
        # (capital_losses_allowed_against_gains) plus a net loss limited per
        # return (limited_capital_loss). Those federal amounts are taken out
        # and each non-dependent's line D amount is put in. Only what federal AGI
        # actually holds is taken out: a reform that drops a source from
        # gross income or the loss deduction from the above-the-line list
        # leaves nothing to reverse. Line D still counts gains left out of
        # federal AGI, as ARS 43-1072(H)(6)(b) adds them back.
        p = parameters(period).gov.irs
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        gross_income_sources = p.gross_income.sources
        capital_gains_in_agi = 0
        for source in ["capital_gains", "non_sch_d_capital_gains"]:
            if source in gross_income_sources:
                capital_gains_in_agi += max_(0, person(source, period))
        federal_capital_gains = tax_unit.sum(not_dependent * capital_gains_in_agi)
        if "loss_ald" in p.ald.deductions:
            # loss_ald adds limited_business_loss (section 461(l)) and the two
            # capital parts. Its capital part is what remains after the
            # business part, at most the two capital parts, so a supplied
            # loss_ald, or a replacement formula built on
            # limited_business_loss, that holds business losses only is not
            # read as a capital deduction. A replacement that computes its
            # own business losses should replace limited_business_loss too.
            federal_capital_loss = clip(
                tax_unit("loss_ald", period)
                - tax_unit("limited_business_loss", period),
                0,
                add(
                    tax_unit,
                    period,
                    ["capital_losses_allowed_against_gains", "limited_capital_loss"],
                ),
            )
        else:
            federal_capital_loss = 0
        line_d = tax_unit.sum(
            not_dependent * person("az_property_tax_credit_capital_gains", period)
        )

        # Not floored at zero: household income (Form 140PTC line J) can be
        # negative, and az_property_tax_credit treats it as zero only for the
        # Schedule 1 and 2 lookup.
        return (
            federal_agi
            - taxable_social_security
            - federal_capital_gains
            + federal_capital_loss
            + line_d
        )
