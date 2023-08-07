from policyengine_us.model_api import *


class vt_retirement_income_exemption(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont retirement income exemption"
    reference = [
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(B)(iv)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=3",  # Instruction for 2022 SCHEDULE IN-112 - RETIREMENT INCOME EXEMPTION WORKSHEET
    ]
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont retirement benefits exempt from Vermont taxation."

    def formula(tax_unit, period, parameters):
        # Filers with no taxable social security benefit reported on federal Form 1040 aren't qualified for this exemption. (SECTION I Q1)
        # Filing jointly with agi more than 75,000 or other filing statuses with agi more than 60,000 also isn't qualified. (SECTION I Q2)
        tax_unit_taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("vt_agi", period)
        p = parameters(period).gov.states.vt.tax.income.agi
        # List of non qualified tax unit
        non_qualified = (tax_unit_taxable_social_security == 0) | (
            agi >= p.qualification[filing_status]
        )
        # Filing jointly with agi less than $65,000 or other filing statuses with agi less than $50,000 are fully qualified for this exemption. (SECTION I Q3)
        fully_qualified = agi < p.threshold[filing_status]
        # Filing jointly with agi between $65,000-$75,000 or other filing statuses with agi between $50,000-$60,000 are partially qualified for this exemption. (SECTION II)
        partial_qualified = (agi >= p.threshold[filing_status]) & (
            agi < p.qualification[filing_status]
        )
        # Calculate parital exemption amount
        partial_exemption_ratio = min_(
            round_(max_(p.threshold[filing_status] - agi, 0) / 10000, 2), 1
        )
        partial_exemption = (
            tax_unit_taxable_social_security * partial_exemption_ratio
        )

        return select(
            [non_qualified, partial_qualified, fully_qualified],
            [0, partial_exemption, tax_unit_taxable_social_security],
        )
