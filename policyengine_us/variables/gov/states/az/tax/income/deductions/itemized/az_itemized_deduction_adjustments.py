from policyengine_us.model_api import *


class az_itemized_deduction_adjustments(Variable):
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
        line1 = add(tax_unit, period, ["medical_expense"])
        medical = parameters(period).gov.irs.deductions.itemized.medical
        line2 = medical.floor * tax_unit("positive_agi", period)
        line3 = line1 - line2 if line1 >= line2 else 0
        line4 = line2 - line1 if line2 > line1 else 0
        
        # Adjustment to Interest Deduction
        # line5=If you received a federal credit for interest paid on mortgage credit certificates (from federal Form 8396),
        #  enter the amount of mortgage interest you paid for 2022 that is equal to the amount of your 2022federal credit.
        line5 = 0
        # Currently, I considere it is 0 since I didn't find anything in variable.gov.irs.income.taxable_income.deductions.itemizing

        # Adjustments to Charitable Contributions
        # Amount of charitable contributions for which you are claiming a credit under Arizona law
        # I assume it is the same as federal law
        line6 = tax_unit("charitable_deduction", period)

        # If yes, line7=0. I assume we claim income taxes on federal Sechedule A.
        line1A = tax_unit("state_and_local_sales_or_income_tax", period)
        # line2A= Amount included in the line 1A for which you claimed an Arizona credit
        line2A = tax_unit("az_total_credit", period)
        line3A = line1A - line2A
        p = parameters(period).gov.states.az.tax.income.deductions.itemized
        filing_status = tax_unit("filing_status", period)
        line4A = p.itemized_deduction_limit[filing_status]
        line5A = min_(line3A, line4A)
        line6A = tax_unit("salt_deduction", period)
        line7 = line6A - line5A

        # This part was marked as not included after meeting
        line8 = 0

        # adjusted itemized deduction
        line9 = line3 + line5
        line10 = line4 + line6 + line7 + line8
        # line11=Total federal itemized deductions allowed to be taken on federal return
        line11 = tax_unit("az_total_allowed_itemized_deduction_irs", period)
        line12 = line9
        line13 = line11 + line12
        line14 = line10
        return max_(line13 - line14, 0)
