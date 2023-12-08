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
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.standard.tier_three
        filing_status = tax_unit("filing_status", period)
        # Exemption(s), taxable Social Security benefits,
        # military compensation (including retirement benefits),
        # Michigan National Guard retirement benefits and railroad
        # retirement benefits included in AGI may reduce the amount
        # eligible to be claimed on this deduction.
        person = tax_unit.members
        uncapped_pension_income = person("taxable_pension_income", period)
        reductions = add(
            person,
            period,
            [
                "military_retirement_pay",
                "military_service_income",
                "taxable_social_security",
            ],
        )
        mi_exemptions = tax_unit("mi_exemptions", period)

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        cap_reduction = tax_unit.sum(reductions * is_head_or_spouse)
        cap = max_(
            p.amount[filing_status] - cap_reduction - mi_exemptions,
            0,
        )

        return min_(
            tax_unit.sum(uncapped_pension_income * is_head_or_spouse), cap
        )
