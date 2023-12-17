from policyengine_us.model_api import *


class mi_standard_deduction_tier_two(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan tier two standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(b) & (c)
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=15",
    )
    defined_for = "mi_standard_deduction_tier_two_eligible"

    def formula(tax_unit, period, parameters):
        # First: add the base amount, based on filing status
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.standard.tier_two
        filing_status = tax_unit("filing_status", period)
        base_amount = p.amount.base[filing_status]
        # Next: add the additional amount based on the number of qualifying people
        # If you checked either box 23C or 23G your standard deduction is increased
        eligible_people = tax_unit(
            "mi_standard_deduction_tier_two_increase_eligible_people", period
        )
        increased_amount = p.amount.increase * eligible_people
        increased_base_amount = base_amount + increased_amount
        # After that we reduce the amount by the amounts from line 11 and line 14
        # just applicable to head and spouse
        person = tax_unit.members
        military_pay = add(
            person,
            period,
            ["military_retirement_pay", "military_service_income"],
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        head_or_spouse_military_pay = tax_unit.sum(
            military_pay * is_head_or_spouse
        )
        return max_(increased_base_amount - head_or_spouse_military_pay, 0)
