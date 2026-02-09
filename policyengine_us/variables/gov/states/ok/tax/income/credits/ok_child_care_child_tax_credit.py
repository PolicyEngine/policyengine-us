from policyengine_us.model_api import *


class ok_child_care_child_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma Child Care/Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2025 Form 511-NR instructions, page 11
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=11",
    )
    defined_for = StateCode.OK
    documentation = """
    Oklahoma Child Care/Child Tax Credit.

    Oklahoma offers a combined credit that allows taxpayers to claim the
    GREATER of two possible credits:
    1. 20% of the federal Child and Dependent Care Credit (CDCC)
    2. 5% of the federal Child Tax Credit (CTC)

    Eligibility requirements:
    - Federal AGI must be $100,000 or less
    - Credit is prorated based on OK AGI / Federal AGI ratio

    Calculation steps:
    1. Check AGI eligibility (federal AGI <= $100,000)
    2. Calculate OK CDCC: federal_cdcc_potential * 20%
    3. Calculate OK CTC: federal_ctc_value * 5%
    4. Take the greater of OK CDCC or OK CTC
    5. Prorate by (OK AGI / Federal AGI)

    Example 1 - CDCC is greater:
    - Federal AGI: $60,000 (eligible)
    - Federal CDCC potential: $2,000
    - Federal CTC: $4,000
    - OK CDCC: $2,000 * 20% = $400
    - OK CTC: $4,000 * 5% = $200
    - Credit (before proration): max($400, $200) = $400

    Example 2 - CTC is greater:
    - Federal AGI: $60,000 (eligible)
    - Federal CDCC potential: $500
    - Federal CTC: $6,000
    - OK CDCC: $500 * 20% = $100
    - OK CTC: $6,000 * 5% = $300
    - Credit (before proration): max($100, $300) = $300

    Note: Uses cdcc_potential (not actual CDCC) because Oklahoma matches
    the potential credit amount regardless of federal tax liability.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income.credits
        # Step 1: Determine AGI eligibility (must be <= $100,000)
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi <= p.child.agi_limit
        # Step 2: Calculate OK CDCC amount (20% of federal potential)
        # Oklahoma matches the potential federal credit, not the actual credit
        us_cdcc = tax_unit("cdcc_potential", period)
        ok_cdcc = us_cdcc * p.child.cdcc_fraction
        # Step 3: Calculate OK CTC amount (5% of federal CTC)
        us_ctc = tax_unit("ctc_value", period)
        ok_ctc = us_ctc * p.child.ctc_fraction
        # Step 4: Compute proration ratio (OK AGI / Federal AGI)
        ok_agi = tax_unit("ok_agi", period)
        # Use a mask rather than where to avoid a divide-by-zero warning
        agi_ratio = np.zeros_like(us_agi)
        mask = us_agi != 0
        agi_ratio[mask] = ok_agi[mask] / us_agi[mask]
        prorate = min_(1, max_(0, agi_ratio))
        # Step 5: Return greater of OK CDCC or OK CTC, prorated, if eligible
        return agi_eligible * prorate * max_(ok_cdcc, ok_ctc)
