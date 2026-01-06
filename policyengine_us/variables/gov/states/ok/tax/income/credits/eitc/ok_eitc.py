from policyengine_us.model_api import *


class ok_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2025 Form 511-EIC instructions
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-EIC.pdf",
        # Oklahoma Statutes 68 O.S. Section 2357.43 - Earned Income Tax Credit
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    defined_for = StateCode.OK
    documentation = """
    Oklahoma Earned Income Tax Credit (EITC).

    Oklahoma provides a state EITC equal to 5% of the federal EITC amount,
    but uses FROZEN 2020 federal EITC parameters rather than current year
    parameters. This is a unique feature of Oklahoma's EITC.

    Per 68 O.S. Section 2357.43: The Oklahoma credit is calculated using
    the federal EITC parameters that were in effect for tax year 2020,
    regardless of the current tax year.

    2020 Federal EITC Parameters (frozen for Oklahoma):
    - Maximum credit (0 children): $538
    - Maximum credit (1 child): $3,584
    - Maximum credit (2 children): $5,920
    - Maximum credit (3+ children): $6,660

    Calculation steps:
    1. Compute federal EITC using 2020 parameters (ok_federal_eitc)
    2. Calculate proration ratio: OK AGI / Federal AGI (capped at 0-100%)
    3. Multiply: federal_eitc * 5% * proration_ratio

    Example for 2025 (single filer, 2 children, $30,000 earnings):
    - Federal EITC (2020 params): $4,420
    - Oklahoma match rate: 5%
    - Proration (assume 100% OK income): 1.0
    - Oklahoma EITC: $4,420 * 0.05 * 1.0 = $221

    Note: The proration ensures part-year or nonresident filers receive
    a credit proportional to their Oklahoma-source income.
    """

    def formula(tax_unit, period, parameters):
        # Calculate proration ratio based on OK AGI vs Federal AGI
        us_agi = tax_unit("adjusted_gross_income", period)
        ok_agi = tax_unit("ok_agi", period)
        agi_ratio = np.zeros_like(us_agi)
        mask = us_agi != 0
        agi_ratio[mask] = ok_agi[mask] / us_agi[mask]
        # Proration must be between 0 and 1
        prorate = min_(1, max_(0, agi_ratio))
        # Get federal EITC computed using frozen 2020 parameters
        federal_eitc = tax_unit("ok_federal_eitc", period)
        p = parameters(period).gov.states.ok.tax.income.credits.earned_income
        # Oklahoma EITC = 5% of federal EITC, prorated
        return prorate * p.eitc_fraction * federal_eitc
