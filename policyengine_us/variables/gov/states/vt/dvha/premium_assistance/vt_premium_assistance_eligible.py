from policyengine_us.model_api import *


class vt_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Vermont Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://legislature.vermont.gov/statutes/section/33/018/01812",
        "https://info.healthconnect.vermont.gov/financial-help",
        "https://info.healthconnect.vermont.gov/sites/vhc/files/documents/2027-Eligibility-Income-Thresholds-for-QHP-Subsidies.pdf#page=1",
        # PDF page 2 in Adobe Reader (dynamic XFA form): Section VII applies
        # "ONLY if HH income is at or below 300% FPL", with the household FPL
        # percentage computed as income / FPL x 100, untruncated.
        "https://info.healthconnect.vermont.gov/sites/vhc/files/documents/205APTC-EW-2027.pdf#page=2",
    )
    documentation = (
        "A tax unit is eligible for Vermont Premium Assistance when the program "
        "is in effect, at least one member is eligible for the federal ACA "
        "premium tax credit (which embeds on-Marketplace enrollment, the "
        "married-filing-separately exclusion, and the federal required-"
        "contribution income test), and household income is at or below 300% of "
        "the federal poverty line, measured as the exact ratio of ACA MAGI to "
        "aca_fpg (the prior-year guideline for the section 36B tax family) "
        "rather than the truncated aca_magi_fraction. "
        "Vermont imposes no minimum-income floor, so "
        "the low end is governed by the federal PTC gate, which Vermont "
        "inherits rather than overrides. Since the federal below-poverty "
        "exception for lawfully present immigrants ended after 2025 (Public "
        "Law 119-21, Section 71302), that gate starts at 100% of the federal "
        "poverty line."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.dvha.premium_assistance
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC.
        aptc_eligible = tax_unit.any(tax_unit.members("is_aca_ptc_eligible", period))
        # 33 V.S.A. 1812(a)(1) covers income "less than or equal to 300
        # percent of federal poverty level". Test the exact ratio, not the
        # truncated aca_magi_fraction: truncation maps 300.00%-300.99% to
        # 3.00, which would admit incomes above 300%. The poverty line is
        # aca_fpg, the line aca_magi_fraction and the federal credit divide
        # by, because the program covers those eligible for that credit.
        magi = max_(tax_unit("aca_magi", period), 0)
        fpg = tax_unit("aca_fpg", period)
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it.
        exact_magi_frac = magi.astype(np.float64) / fpg
        income_eligible = exact_magi_frac <= p.fpl_limit
        return in_effect & aptc_eligible & income_eligible
