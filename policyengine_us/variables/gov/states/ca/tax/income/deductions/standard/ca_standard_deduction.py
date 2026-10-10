from policyengine_us.model_api import *


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
        standard = p.amount[filing_status]
        # RTC 17073.5 applies the IRC 63(c)(5) limit, and the Form 540
        # worksheet for dependents applies "only if your parent, or someone
        # else, can claim you (or your spouse/RDP) as a dependent": the
        # deduction is the smaller of the California amount and the larger of
        # the federal minimum or earned income plus the federal addition
        # (line 1 carries line 2 of the federal worksheet).
        dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        p_dependent = parameters(period).gov.irs.deductions.standard.dependent
        # Federal worksheet earned income: wages and self-employment income
        # minus the deductible part of self-employment tax.
        earned_income = max_(
            tax_unit("tax_unit_earned_income", period)
            - tax_unit("self_employment_tax_ald", period),
            0,
        )
        dependent_standard = min_(
            standard,
            max_(
                p_dependent.amount,
                earned_income + p_dependent.additional_earned_income,
            ),
        )
        return where(dependent_elsewhere, dependent_standard, standard)
