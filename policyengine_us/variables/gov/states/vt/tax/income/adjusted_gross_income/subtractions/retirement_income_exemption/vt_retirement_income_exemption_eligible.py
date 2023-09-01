from policyengine_us.model_api import *


class VTRetireExemptionEligibilityStatus(Enum):
    FULLY_QUALIFIED = 1
    PARTIAL_QUALIFIED = 2
    NOT_QUALIFIED = 3


class vt_retirement_income_exemption_eligible(Variable):
    value_type = Enum
    possible_values = VTRetireExemptionEligibilityStatus
    default_value = VTRetireExemptionEligibilityStatus.NOT_QUALIFIED
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont retirement income exemption eligibility status"
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(B)(iv)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=3",  # Instruction for 2022 SCHEDULE IN-112 - RETIREMENT INCOME EXEMPTION WORKSHEET
    )
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont filers use below criteria to check whether the tax unit is eligible for vermont retirement income exemption."

    def formula(tax_unit, period, parameters):
        tax_unit_taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.retirement_income_exemption

        # List of non qualified tax unit (SECTION I Q1,Q2)
        non_qualified = (tax_unit_taxable_social_security == 0) | (
            agi >= p.income_threshold[filing_status]
        )

        # List of fully qualified tax unit (SECTION I Q3)
        fully_qualified = agi < p.reduction_threshold[filing_status]

        # List of partial qualified tax unit(SECTION II)
        partial_qualified = (agi >= p.reduction_threshold[filing_status]) & (
            agi < p.income_threshold[filing_status]
        )

        # Based on the criteria, return the eligibility status.
        return select(
            [non_qualified, partial_qualified, fully_qualified],
            [
                VTRetireExemptionEligibilityStatus.NOT_QUALIFIED,
                VTRetireExemptionEligibilityStatus.PARTIAL_QUALIFIED,
                VTRetireExemptionEligibilityStatus.FULLY_QUALIFIED,
            ],
        )
