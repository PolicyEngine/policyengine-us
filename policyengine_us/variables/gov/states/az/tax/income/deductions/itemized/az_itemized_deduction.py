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
        # mortgage_interest = If you received a federal credit for interest paid on mortgage credit certificates (from federal Form 8396),
        #  enter the amount of mortgage interest you paid for 2022 that is equal to the amount of your 2022federal credit.
        mortgage_interest = 0

        # Adjustments to Charitable Contributions
        # Amount of charitable contributions for which you are claiming a credit under Arizona law
        # I assume it is the same as federal law
        charitable_deduction = tax_unit("charitable_deduction", period)

        # I assume we claim income taxes on federal Sechedule A.
        state_income_tax_before_federal_limitation = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        # line2A= Amount included in the line 1A for which you claimed an Arizona credit
        line2A = tax_unit("az_total_credit", period)
        line3A = state_income_tax_before_federal_limitation - line2A
        p = parameters(period).gov.states.az.tax.income.deductions.itemized
        filing_status = tax_unit("filing_status", period)
        federal_schedule_limit = p.itemized_deduction_limit[filing_status]
        line5A = min_(line3A, federal_schedule_limit)
        salt_deduction = tax_unit("salt_deduction", period)
        adjustment_to_state_income_taxes = salt_deduction - line5A

        # This part was marked as not included after meeting
        other_adjustments = 0

        # adjusted itemized deduction
        line9 = medical_expense_larger_then_irs_allowed + mortgage_interest
        line10 = (
            medical_expense_less_then_irs_allowed
            + charitable_deduction
            + adjustment_to_state_income_taxes
            + other_adjustments
        )
        az_itemized_deductions_less_salt = tax_unit("az_itemized_deductions_less_salt", period)
        line12 = line9
        line13 = az_itemized_deductions_less_salt + line12
        line14 = line10
        return max_(line13 - line14, 0)
