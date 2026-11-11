from policyengine_us.model_api import *


def ca_dependent_standard_deduction_limit(tax_unit, period, parameters, amount):
    """Apply the California Standard Deduction Worksheet for Dependents.

    RTC 17073.5(c)(2) applies the IRC 63(c)(5) limit, and the Form 540
    worksheet for dependents applies "only if your parent, or someone else,
    can claim you (or your spouse/RDP) as a dependent": the deduction is the
    smaller of the California amount and the larger of the federal minimum
    or earned income plus the federal addition (line 1 carries line 2 of the
    federal worksheet).
    """
    dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
    p = parameters(period).gov.irs.deductions.standard.dependent
    earned_income = tax_unit("dependent_standard_deduction_earned_income", period)
    limit = max_(p.amount, earned_income + p.additional_earned_income)
    return where(dependent_elsewhere, min_(amount, limit), amount)


class ca_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California standard deduction"
    unit = USD
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540.pdf",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17073.5",
        # California Standard Deduction Worksheet for Dependents.
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=13",
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        return ca_dependent_standard_deduction_limit(
            tax_unit, period, parameters, p.amount[filing_status]
        )
