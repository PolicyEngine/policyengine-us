from policyengine_us.model_api import *


class vt_retirement_income_exemption(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont retirement income exemption"
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(B)(iv)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=3",  # Instruction for 2022 SCHEDULE IN-112 - RETIREMENT INCOME EXEMPTION WORKSHEET
    )
    unit = USD
    defined_for = "vt_retirement_income_exemption_eligible"
    documentation = "Vermont retirement benefits exempt from Vermont taxation."

    def formula(tax_unit, period, parameters):
        # Filer can choose from one of Social Security, Civil Service Retirement System (CSRS), Military Retirement Income
        # or other eligible retirement systems to calculate retirement income exemption
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption
        # Get social security amount
        tax_unit_taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        # Get vt retirement income exclusion from military retirement system
        vt_military_retirement_pay = tax_unit(
            "vt_military_retirement_pay_exclusion", period
        )
        # Get vt retirement income exclusion from CSRS
        vt_csrs_retirement_pay = tax_unit(
            "vt_csrs_retirement_pay_exclusion", period
        )
        # Get vt retirement income exclusion from other certain retirement systems
        vt_other_retirement_pay = tax_unit(
            "vt_other_retirement_pay_exclusion", period
        )

        # Assume that filers will always choose the largest reitrement income exclusion from various retirement system
        chosen_retirement_income = max_(
            tax_unit_taxable_social_security,
            vt_military_retirement_pay,
            vt_csrs_retirement_pay,
            vt_other_retirement_pay,
        )

        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)

        # List of fully qualified tax unit (SECTION I Q3)
        fully_qualified = agi < p.threshold.reduction[filing_status]

        # List of partial qualified tax unit(SECTION II)
        partial_qualified = (agi >= p.threshold.reduction[filing_status]) & (
            agi < p.threshold.income[filing_status]
        )

        # Calculate the exemption ratio
        partial_exemption_ratio = max_(
            p.threshold.income[filing_status] - agi, 0
        ) / (p.divisor)

        # Round the exemption ratio to two decimal point
        partial_exemption_ratio = round_(partial_exemption_ratio, 2)

        # The exemption ratio should be below one
        partial_exemption_ratio = min_(partial_exemption_ratio, 1)

        # Calculate parital exemption amount
        partial_exemption = chosen_retirement_income * partial_exemption_ratio

        # Return final exemption amount based on eligibility status
        return select(
            [partial_qualified, fully_qualified],
            [partial_exemption, chosen_retirement_income],
        )
