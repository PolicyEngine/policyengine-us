from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_one(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction for tier one"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (1)(f)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = "mi_retirement_benefits_deduction_tier_one_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_one
        filing_status = tax_unit("filing_status", period)

        person = tax_unit.members
        # "Recipients born before 1946 may subtract all qualifying retirement and
        # pension benefits received from federal or Michigan public sources"
        # all public benefits can be deducted
        uncapped_public_benefits = person(
            "taxable_public_pension_income", period
        )
        # deductable private benefits are capped
        uncapped_private_benefits = person(
            "taxable_private_pension_income", period
        )
        # the cap is reduced by the amount of military retirement pay
        military_retirement_pay = person("military_retirement_pay", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        cap_reduction = tax_unit.sum(
            military_retirement_pay * is_head_or_spouse
        )
        cap = max_(p.amount[filing_status] - cap_reduction, 0)
        # If your public retirement benefits are greater than the maximum amount,
        # you are not entitled to claim an additional subtraction for private pensions.
        capped_public_benefits = max_(
            cap - tax_unit.sum(uncapped_public_benefits * is_head_or_spouse), 0
        )
        capped_private_benefits = min_(
            tax_unit.sum(uncapped_private_benefits * is_head_or_spouse),
            capped_public_benefits,
        )

        return (
            tax_unit.sum(uncapped_public_benefits * is_head_or_spouse)
            + capped_private_benefits
        )
