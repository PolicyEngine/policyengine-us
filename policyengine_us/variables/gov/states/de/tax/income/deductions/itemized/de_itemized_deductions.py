from policyengine_us.model_api import *


class de_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=7"
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=11"
        "https://casetext.com/statute/delaware-code/title-30-state-taxes/part-ii-income-inheritance-and-estate-taxes/chapter-11-personal-income-tax/subchapter-ii-resident-individuals/section-1109-itemized-deductions-for-application-of-this-section-see-66-del-laws-c-86-section-8"
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.itemized
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction
            not in [
                "interest_deduction",
                "charitable_deduction",
            ]
        ]
        federal_deductions = add(tax_unit, period, deductions)

        de_donation = add(
            tax_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )

        de_interest = add(
            tax_unit,
            period,
            ["mortgage_interest", "investment_income_form_4952"],
        )

        return federal_deductions + de_donation + de_interest
