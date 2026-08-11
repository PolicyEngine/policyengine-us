from policyengine_us.model_api import *


class vt_retirement_income_exemption(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont retirement income exemption"
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(B)(iv)
        "https://legislature.vermont.gov/statutes/section/32/151/05830e"  # Titl. 32 V.S.A. § 5830e
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=3",  # Instruction for 2022 SCHEDULE IN-112 - RETIREMENT INCOME EXEMPTION WORKSHEET
        "https://tax.vermont.gov/individuals/seniors-and-retirees",  # Instruction for exemption from different retirement system
    )
    unit = USD
    documentation = "Vermont retirement benefits exempt from Vermont taxation."
    defined_for = "vt_retirement_income_exemption_eligible"

    def formula(tax_unit, period, parameters):
        # Filer can choose from one of Social Security,
        # Civil Service Retirement System (CSRS), Military Retirement Income
        # or other eligible retirement systems
        # to determine eligibility and calculate retirement income exemption.

        # Get social security amount
        tax_unit_taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        # Get vt retirement income exclusion from military retirement system
        vt_military_retirement_pay_exclusion = tax_unit(
            "vt_military_retirement_pay_exclusion", period
        )
        # Get vt retirement income exclusion from CSRS
        vt_csrs_retirement_pay_exclusion = tax_unit(
            "vt_csrs_retirement_pay_exclusion", period
        )
        # Assume that filers will always choose the largest reitrement income
        # exclusion from various retirement system
        larger_retirement_income = max_(
            tax_unit_taxable_social_security,
            vt_military_retirement_pay_exclusion,
        )
        chosen_retirement_income = max_(
            larger_retirement_income, vt_csrs_retirement_pay_exclusion
        )
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        # Get which retirement system the filer use
        use_ss = tax_unit_taxable_social_security == chosen_retirement_income
        # Get which parameter file to use
        p = parameters(period).gov.states.vt.tax.income.agi.retirement_income_exemption
        reduction_start = where(
            use_ss,
            p.social_security.reduction.start[filing_status],
            p.csrs.reduction.start[filing_status],
        )
        reduction_end = where(
            use_ss,
            p.social_security.reduction.end[filing_status],
            p.csrs.reduction.end[filing_status],
        )
        # List of partial qualified tax unit(SECTION II)
        partial_qualified = (
            (agi >= reduction_start)
            & (agi < reduction_end)
            & (chosen_retirement_income != 0)
        )
        # Calculate the exemption ratio
        partial_exemption_ratio = max_(reduction_end - agi, 0) / p.divisor
        # Round the exemption ratio to two decimal point
        partial_exemption_ratio = round_(partial_exemption_ratio, 2)
        # The exemption ratio should be below one
        partial_exemption_ratio = min_(partial_exemption_ratio, 1)
        # Calculate parital exemption amount
        partial_exemption = chosen_retirement_income * partial_exemption_ratio
        csrs_or_ss_exemption = where(
            partial_qualified, partial_exemption, chosen_retirement_income
        )
        # The 2025 income-based military exclusion (32 V.S.A. 5830e(d)) has its own
        # $125k-$175k phase-out inside vt_military_retirement_income_based_exemption,
        # so when it is the chosen exclusion it bypasses the CSRS reduction band
        # rather than being phased a second time.
        use_military = ~use_ss & (
            vt_military_retirement_pay_exclusion == chosen_retirement_income
        )
        military_income_based = p.military_retirement.income_based_structure.in_effect
        bypass_csrs_band = use_military & military_income_based
        return where(bypass_csrs_band, chosen_retirement_income, csrs_or_ss_exemption)
