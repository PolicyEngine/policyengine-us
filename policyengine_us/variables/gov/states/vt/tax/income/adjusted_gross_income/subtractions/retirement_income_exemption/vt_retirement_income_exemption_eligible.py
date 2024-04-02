from policyengine_us.model_api import *


class vt_retirement_income_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont retirement income exemption eligibility status"
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(B)(iv)
        "https://legislature.vermont.gov/statutes/section/32/151/05830e"  # Titl. 32 V.S.A. § 5830e
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=3",  # Instruction for 2022 SCHEDULE IN-112 - RETIREMENT INCOME EXEMPTION WORKSHEET
        "https://tax.vermont.gov/individuals/seniors-and-retirees",  # Instruction for exemption from different retirement system
    )
    defined_for = StateCode.VT
    documentation = "Vermont filers use below criteria to check whether the tax unit is eligible for vermont retirement income exemption."

    def formula(tax_unit, period, parameters):
        # Filer can choose from one of Social Security,
        # Civil Service Retirement System (CSRS), Military Retirement Income
        # or other eligible retirement systems to determine eligibility
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption.csrs.reduction
        # One of the retirement income should be greater than 0
        retirement_income = add(
            tax_unit,
            period,
            [
                "tax_unit_taxable_social_security",
                "military_retirement_pay",
                "csrs_retirement_pay",
            ],
        )
        retirement_income_qualified = retirement_income > 0
        # The agi should below threshold
        agi_qualified = agi < p.end[filing_status]
        # Both qualified then the filer is qualified for vermont retirement
        # income exemption
        return retirement_income_qualified & agi_qualified
