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
    defined_for = StateCode.VT
    documentation = "Vermont retirement benefits exempt from Vermont taxation."

    def formula(tax_unit, period, parameters):
        tax_unit_taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption

        # Get eligibility status
        eligible = tax_unit("vt_retirement_income_exemption_eligible", period)

        # List of fully qualified tax unit (SECTION I Q3)
        fully_qualified = (agi < p.threshold.reduction[filing_status]) & (
            eligible
        )

        # List of partial qualified tax unit(SECTION II)
        partial_qualified = (
            (agi >= p.threshold.reduction[filing_status])
            & (agi < p.threshold.income[filing_status])
            & (eligible)
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
        partial_exemption = (
            tax_unit_taxable_social_security * partial_exemption_ratio
        )

        return select(
            [~eligible, partial_qualified, fully_qualified],
            [0, partial_exemption, tax_unit_taxable_social_security],
        )
