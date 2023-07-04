from policyengine_us.model_api import *


class az_itemized_deduction_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona itemized deduction adjustments"
    unit = USD
    documentation = "Arizona Form 140 Schedule A"
    reference = (
        "https://azdor.gov/forms/individual/itemized-deduction-adjustments-form"
        "https://azdor.gov/forms/individual/form-140-resident-personal-income-tax-form-calculating"
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # itemizing = tax_unit("tax_unit_itemizes", period)
        us_p = parameters(period).gov.irs.deductions

        # Adjustment to Medical and Dental Expenses
        # from medical_expense_deduction.py in irs
        line1_medical_expense = tax_unit("medical_expense", period) 
        medical = parameters(period).gov.irs.deductions.itemized.medical
        line2_medical_floor = medical.floor * tax_unit("positive_agi", period)
        line3_4_adjustments_medical=abs_(expense - medical_floor)

        # Adjustment to Interest Deduction
        # line5=enter the amount of mortgage interest you paid for 2022 that is equal to the amount of your 2022 federal credit

        # Adjustments to Charitable Contributions
        # Amount of charitable contributions for which you are claiming a credit under Arizona law
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        non_cash_donations = add(tax_unit, period, ["charitable_non_cash_donations"])
        line6 = cash_donations+non_cash_donations


        # Adjustment to State Income Taxes
        line1A=tax_unit("az_income_tax_before_credits", period) 
        # line2A= Amount included in the line 1A for which you claimed an Arizona credit
        line3A = line1A-line2A
        p = parameters(period).gov.states.az.tax.income.deductions.itemized
        line4A = p.limit_from_federal_schedule_a[filing_status]
        line5A = min_(line3A, line4A)
        # line6A = Enter total state income taxes claimed on federal Schedule A (after limitation)
        line7 = line6A-line5A

        # Other Adjustments
        # line8 = Amount allowed as a federal itemized deduction that relates to income not subject to Arizona tax

        # adjusted itemized deduction
        line9=line3+line5
        line10=line4+line6+line7+line8
        # line11=Total federal itemized deductions allowed to be taken on federal return
        line12 = line9
        line13 = line11+line12
        line14 = line10
        return max_(line13 - line14, 0)







