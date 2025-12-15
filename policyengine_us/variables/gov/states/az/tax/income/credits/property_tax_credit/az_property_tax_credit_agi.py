from policyengine_us.model_api import *


class az_property_tax_credit_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona adjusted gross income for property tax credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Adjusted gross income as defined for Arizona property tax credit purposes. "
        "Per ARS 43-1072(H)(6) and ITR 12-1, this starts with Federal AGI and only "
        "excludes items specifically listed in ARS 43-1072(I): Social Security, "
        "railroad retirement, workers compensation, Arizona unemployment, veterans "
        "disability pensions, welfare, and gifts. Unlike regular Arizona income tax, "
        "this does NOT exclude pension income, capital gains, or Arizona exemptions."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072
        "https://azdor.gov/sites/default/files/2023-03/RULINGS_INDV_2012_itr12-1.pdf",  # ITR 12-1
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
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )

        # NOTE: We do NOT subtract Arizona's regular subtractions here because:
        # - Pension exclusions (az_public_pension_exclusion,
        #   az_military_retirement_subtraction) should be INCLUDED per
        #   ITR 12-1 item (9)
        # - Capital gains subtraction (az_long_term_capital_gains_subtraction)
        #   should be INCLUDED per ITR 12-1 item (7)
        # - US Government interest should be INCLUDED per ITR 12-1 item (2)
        # - Arizona exemptions (aged, blind) should NOT be subtracted

        return max_(0, federal_agi - taxable_social_security)
