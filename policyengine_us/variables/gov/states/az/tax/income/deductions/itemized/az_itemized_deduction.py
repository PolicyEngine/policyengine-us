from policyengine_us.model_api import *

class az_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona itemized deduction adjustments"
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
        us_p = parameters(period).gov.irs.deductions
        medical_expense = add(tax_unit, period, ["medical_expense"])
        medical = parameters(period).gov.irs.deductions.itemized.medical
        medical_expense_irs = medical.floor * tax_unit("positive_agi", period)
        medical_expense_larger_then_irs_allowed = where(
            medical_expense >= medical_expense_irs,
            medical_expense - medical_expense_irs,
            0,
        )
        medical_expense_less_then_irs_allowed = where(
            medical_expense_irs > medical_expense,
            medical_expense_irs - medical_expense,
            0,
        )

        # Adjustment to Interest Deduction
        # mortgage_interest = the amount of mortgage interest you paid for 2022 that is equal to
        # the amount of federal credit, if you received a federal credit for interest paid on
        # mortgage credit certificates (from federal Form 8396).

        # Adjustments to Charitable Contributions
        # Amount of charitable contributions for which you are claiming a credit under Arizona law
        # I assume it is the same as federal law
        charitable_deduction = tax_unit("charitable_deduction", period)

        # I assume we claim income taxes on federal Sechedule A.
        state_income_tax_before_federal_limitation = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        # line2A= Amount included in the line 1A for which you claimed an Arizona credit
        az_total_credit = tax_unit("az_total_credit", period)
        diff = state_income_tax_before_federal_limitation - az_total_credit
        p = parameters(period).gov.states.az.tax.income.deductions.itemized
        filing_status = tax_unit("filing_status", period)
        federal_schedule_limit = p.itemized_deduction_limit[filing_status]
        line5A = min_(diff, federal_schedule_limit)
        salt_deduction = tax_unit("salt_deduction", period)
        adjustment_to_state_income_taxes = salt_deduction - line5A

        # This part was marked as not included after meeting
        # other_adjustments = 0

        # adjusted itemized deduction
        adjustment_medical_mortgage = medical_expense_larger_then_irs_allowed
        # if we have mortgage interest, we need to add mortgage interest into "adjustment_medical_mortgage".
        adjustment_medical_charitable_stateTax_other = (
            medical_expense_less_then_irs_allowed
            + charitable_deduction
            + adjustment_to_state_income_taxes
        )  
        # If you have other_adjustments, we need to add "other_adjustments" into "adjustment_medical_charitable_stateTax_other"
        az_itemized_deductions_less_salt = tax_unit(
            "az_itemized_deductions_less_salt", period
        )
        # line12 = adjustment_medical_mortgage
        line13 = az_itemized_deductions_less_salt + adjustment_medical_mortgage
        line14 = adjustment_medical_charitable_stateTax_other
        return max_(line13 - line14, 0)