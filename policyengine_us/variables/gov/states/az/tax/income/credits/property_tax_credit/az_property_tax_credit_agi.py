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
        "a net loss limited per member, instead of federal AGI's net capital gain "
        "less a capital loss limited per return. Covers members who are not "
        "dependents, as federal AGI does, and can be negative."
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

        # Capital gains and losses (Form 140PTC Part 1 line D). Federal AGI
        # adds each non-dependent's net capital gain (irs_gross_income) and
        # subtracts the capital loss deduction, limited to $3,000 per return
        # (limited_capital_loss, part of loss_ald). A.A.C. R15-2C-502(C)(3)
        # and ITR 12-1 item (7) instead limit each member's net loss to
        # $1,500, so the federal amounts are replaced by each member's line D
        # amount. Dependents' line D amounts are in
        # az_property_tax_credit_dependent_income, with their other income.
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        federal_capital_gains = tax_unit.sum(
            ~is_dependent * max_(0, person("capital_gains", period))
        )
        federal_capital_loss = tax_unit("limited_capital_loss", period)
        line_d = tax_unit.sum(
            ~is_dependent * person("az_property_tax_credit_capital_gains", period)
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
