from policyengine_us.model_api import *


class az_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Itemized Deduction Adjustments"
    unit = USD
    documentation = "Arizona Form 140 Schedule A"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://azdor.gov/forms/individual/itemized-deduction-adjustments-form"
        "https://azdor.gov/forms/individual/form-140-resident-personal-income-tax-form-calculating"
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # Adjustment to Medical and Dental Expresses
        medical_expense = add(tax_unit, period, ["medical_expense"])
        # medical = parameters(period).gov.irs.deductions.itemized.medical (will be deleted later)
        # medical_expense_irs = medical.floor * tax_unit("positive_agi", period)  (will be deleted later)
        medical_expense_deduction =tax_unit("medical_expense_deduction", period)
        medical_expense_larger_then_irs_allowed = where(
            medical_expense >= medical_expense_deduction,
            medical_expense - medical_expense_deduction,
            0,
        )
        medical_expense_less_then_irs_allowed = where(
            medical_expense_deduction > medical_expense,
            medical_expense_deduction - medical_expense,
            0,
        )

        # Adjustment to Interest Deduction
        # mortgage_interest = the amount of mortgage interest you paid for 2022 that is equal to
        # the amount of federal credit, if you received a federal credit for interest paid on
        # mortgage credit certificates (from federal Form 8396).

        # Adjustments to Charitable Contributions
        # Amount of charitable contributions for which you are claiming a credit under Arizona law
        # I assume it is the same as irs after discussing with Pavel
        charitable_deduction = tax_unit("charitable_deduction", period)

        # Adjustment to State Income Taxes
        state_income_tax_before_federal_limitation = tax_unit(
            "state_and_local_sales_or_income_tax", period
        ) # before limitation

        # In above part, the form said "Total state income taxes on the federal Schedule A before applying the federal limitations"
        # I feel like state_income_taxes = tax_unit("federal_state_income_tax", period) may be more appropriate then "state_income_tax_before_federal_limitation"  
        # since only sales or income tax can be itemized, but not both. (from state_and_local_sales_or_income_tax.py)


        # line2A = Amount included in the line 1A for which you claimed an Arizona credit
        # line2A = az_total_credit
        az_total_credit = tax_unit("az_total_credit", period)
        total_state_income_taxes_unclaimed_for_credit = (
            state_income_tax_before_federal_limitation - az_total_credit
        )
        filing_status = tax_unit("filing_status", period)
        federal_schedule_limit = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.cap[filing_status]
        allowed_state_income_taxes_for_credit = min_(
            total_state_income_taxes_unclaimed_for_credit,
            federal_schedule_limit,
        )

        salt_deduction = tax_unit("salt_deduction", period)
        # what is "total state income taxes claimed on federal Schedule A (after limitation)"?
        # Is it just salt_deduction?

        adjustment_to_state_income_taxes = (
            salt_deduction - allowed_state_income_taxes_for_credit
        )

        # Other Adjustments
        # This part was marked as not included after meeting
        # other_adjustments = 0

        # Adjusted Itemized Deduction
        adjustment_medical_mortgage = medical_expense_larger_then_irs_allowed  # + adjusrment_intertest_deduction
        # if we have mortgage interest, we need to add "adjusrment_intertest_deduction" into "adjustment_medical_mortgage"
        adjustment_medical_charitable_stateIncomeTax_other = (
            medical_expense_less_then_irs_allowed
            + charitable_deduction
            + adjustment_to_state_income_taxes
            # + other_adjustments
        )
        # If you have other_adjustments, we need to add "other_adjustments"
        # into "adjustment_medical_charitable_stateIncomeTax_other"
        itemized_deductions_less_salt = tax_unit(
            "itemized_deductions_less_salt", period
        )
        federal_itemized_deduction_with_adjustment_for_medical_and_interest = (
            itemized_deductions_less_salt + adjustment_medical_mortgage
        )
        return max_(
            federal_itemized_deduction_with_adjustment_for_medical_and_interest
            - adjustment_medical_charitable_stateIncomeTax_other,
            0,
        )
