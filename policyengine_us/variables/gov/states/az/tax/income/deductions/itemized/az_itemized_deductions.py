from policyengine_us.model_api import *


class az_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Itemized Deductions"
    unit = USD
    documentation = "Arizona Form 140 Schedule A"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://law.justia.com/codes/arizona/2022/title-43/section-43-1042/",
        "https://azdor.gov/forms/individual/itemized-deduction-adjustments-form",
        "https://azdor.gov/forms/individual/form-140-resident-personal-income-tax-form-calculating",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction
            not in [
                "medical_expense_deduction",
                "charitable_deduction",
            ]
        ]
        federal_deductions = add(tax_unit, period, deductions)
        # Arizona allows a complete deduction for medical and dental expenses
        medical_expenses = add(tax_unit, period, ["medical_expense"])

        # Adjustments to Charitable Contributions
        # Amount of charitable contributions for which you are claiming
        # a credit under Arizona law.
        charitable_deduction = tax_unit("charitable_deduction", period)
        charitable_contributions_credit = tax_unit(
            "az_charitable_contributions_credit", period
        )
        # The charitable deduction is reduced by the amount which is used for the
        # Arizona charitable contributions credit,
        # assuming that the same charitable contributions
        charitable_deduction_after_credit = max_(
            charitable_deduction - charitable_contributions_credit, 0
        )
        # The state and local income tax is reduced by the amount which is used
        # to claim the Arizona charitable contributions credit
        # Since the Arizona charitable contributions credit is based on contributions
        # to qulalifying foster care organizations, we do not reduce the salt deduction
        return (
            federal_deductions
            + medical_expenses
            + charitable_deduction_after_credit
        )
