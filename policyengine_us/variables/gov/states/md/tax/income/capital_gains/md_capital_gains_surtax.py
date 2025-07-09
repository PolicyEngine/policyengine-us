from policyengine_us.model_api import *


class md_capital_gains_surtax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland capital gains surtax"
    definition_period = YEAR
    unit = USD
    reference = [
        "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=162"  # Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025
    ]
    defined_for = "md_capital_gains_surtax_applies"

    def formula(tax_unit, period, parameters):

        p = parameters(period).gov.states.md.tax.income.capital_gains

        # Get net capital gains (sum of long-term and short-term)
        # NOTE: This is the basic implementation using readily available variables
        total_capital_gains = add(
            tax_unit,
            period,
            ["short_term_capital_gains", "long_term_capital_gains"],
        )

        # Apply capital losses (with federal limitation)
        capital_losses = tax_unit("limited_capital_loss", period)
        # Use federal net capital gain calculation which handles loss limitations
        net_capital_gains = max_(total_capital_gains - capital_losses, 0)

        # LIMITATIONS AND MISSING IMPLEMENTATIONS:
        #
        # 1. PRIMARY RESIDENCE EXCLUSION (NOT IMPLEMENTED):
        #    - Should exclude gains from primary residence sales above threshold
        #    - Missing: Section 121 exclusion (amounts vary by filing status)
        #    - Missing: Property sale price tracking
        #    - Missing: Primary residence identification
        #    - Reason: PolicyEngine doesn't currently model detailed property sales
        #
        # 2. RETIREMENT ACCOUNT EXCLUSION (PARTIALLY IMPLEMENTED):
        #    - Current capital_gains variables should already exclude retirement distributions
        #    - Retirement distributions are typically handled separately as ordinary income
        #    - This exclusion should already be working correctly in the current model
        #
        # 3. LIVESTOCK EXCLUSION (NOT IMPLEMENTED):
        #    - Should exclude livestock gains if >50% income from farming/ranching
        #    - Missing: Farming/ranching income classification
        #    - Missing: Livestock vs other business asset identification
        #    - Reason: PolicyEngine doesn't track detailed business asset types
        #
        # 4. CONSERVATION EASEMENT EXCLUSION (NOT IMPLEMENTED):
        #    - Should exclude gains from land under conservation/agricultural/forest easements
        #    - Missing: Property easement status tracking
        #    - Missing: Land use classification system
        #    - Reason: Requires property-specific data not available in tax records
        #
        # 5. IRC § 179 BUSINESS PROPERTY EXCLUSION (NOT IMPLEMENTED):
        #    - Should exclude gains from property eligible for § 179 deduction
        #    - Missing: Business property classification
        #    - Missing: § 179 eligibility determination
        #    - Reason: Requires detailed business asset tracking
        #
        # 6. NONPROFIT AFFORDABLE HOUSING EXCLUSION (NOT IMPLEMENTED):
        #    - Should exclude gains from affordable housing owned by nonprofits
        #    - Missing: Entity type identification (nonprofit vs individual)
        #    - Missing: Affordable housing property classification
        #    - Reason: PolicyEngine focuses on individual/household tax units
        #
        # CURRENT IMPLEMENTATION COVERS:
        # - Basic 2% surtax rate
        # - Federal AGI threshold for surtax
        # - Net capital gains calculation with loss limitations
        # - Retirement account exclusion (implicit in capital_gains variables)
        #
        # ACCURACY IMPACT:
        # - Will overstate surtax liability for taxpayers with excluded gain types
        # - Most significant overstatement likely from primary residence sales
        # - Business-related exclusions may affect fewer taxpayers but could be material

        return net_capital_gains * p.surtax_rate
