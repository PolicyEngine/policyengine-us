from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_net_household_income(Variable):
    value_type = float
    entity = Person
    label = "Net household income for Montana elderly homeowner or renter credit"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_elderly_homeowner_or_renter_credit_eligible"
    reference = (
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        # 2024 Form 2, Schedule 2EC
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=10",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        # Only one claimant per household is entitled to relief
        # (§ 15-30-2341(1)); mt_elderly_homeowner_or_renter_credit_selected_claimant
        # picks the claimant. Married couples living apart may receive only
        # one credit per year (ARM 42.4.302(3)(a)).
        standard_exclusion = p.net_household_income.standard_exclusion
        # Gross household income counts every member of the household,
        # including those outside the claimant's return (§ 15-30-2337(4);
        # 2024 Schedule 2EC line 17). Allocate it to the head.
        head = person("is_tax_unit_head", period)
        gross_household_income = add(
            person.household,
            period,
            ["mt_elderly_homeowner_or_renter_credit_gross_household_income"],
        )
        gross_household_income_head = gross_household_income * head
        reduced_household_income = max_(
            gross_household_income_head - standard_exclusion, 0
        )
        reduction_rate = p.net_household_income.reduction_rate.calc(
            reduced_household_income
        )
        return reduced_household_income * reduction_rate
