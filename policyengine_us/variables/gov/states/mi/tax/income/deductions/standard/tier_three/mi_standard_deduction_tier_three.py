from policyengine_us.model_api import *


class mi_standard_deduction_tier_three(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan tier three standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(e)
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16",
    )
    defined_for = "mi_standard_deduction_tier_three_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.deductions
        # Line 1: enter base amount, based on filing status
        filing_status = tax_unit("filing_status", period)
        base_amount = p.standard.tier_three.amount[filing_status]

        # Exemption(s), taxable Social Security benefits,
        # military compensation (including retirement benefits),
        # Michigan National Guard retirement benefits and railroad
        # retirement benefits included in AGI may reduce the amount
        # eligible to be claimed on this deduction.

        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Line 2: enter military retirement pay
        military_retirement_pay = person("military_retirement_pay", period)
        # Line 3: enter military service income or taxable social security
        taxable_ss = person("taxable_social_security", period)
        military_service_income = person("military_service_income", period)
        larger_ss_or_military_pay = max_(taxable_ss, military_service_income)
        # Line 4 are personal (and stillborn) exemptions
        mi_personal_exemptions = tax_unit("mi_personal_exemptions", period)
        # Line 5: add lines 2 through 4
        total_person_reductions = tax_unit.sum(
            is_head_or_spouse
            * (military_retirement_pay + larger_ss_or_military_pay)
        )
        total_reductions = total_person_reductions + mi_personal_exemptions
        # Line 6: subtract line 5 from line 1
        standard_deduction_tier_three = max_(base_amount - total_reductions, 0)
        # Worksheet 3.3: Retirement and Pension Benefits Subtraction for Section D of Form 4884
        if p.retirement_benefits.expanded.availability:
            expanded_retirement_benefits_deduction = tax_unit(
                "mi_expanded_retirement_benefits_deduction",
                period,
            )
            return max_(
                standard_deduction_tier_three,
                expanded_retirement_benefits_deduction,
            )
        else:
            return standard_deduction_tier_three
