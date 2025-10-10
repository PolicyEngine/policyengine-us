from policyengine_us.model_api import *


class chapter_7_bankruptcy_other_necessary_expenses_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy other necessary expenses deductions"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=5"

    def formula(spm_unit, period, parameters):
        income_tax = spm_unit("spm_unit_federal_tax", period)

        child_support_expense = add(
            spm_unit, period, ["child_support_expense"]
        )
        childcare_expenses = spm_unit("childcare_expenses", period)

        out_of_pocket_healthcare_allowance = spm_unit(
            "chapter_7_bankruptcy_out_of_pocket_health_care_deduction", period
        )
        out_of_pocket_healthcare_expense = add(
            spm_unit, period, ["medical_out_of_pocket_expenses"]
        )
        additional_health_care_expenses = max_(
            out_of_pocket_healthcare_expense
            - out_of_pocket_healthcare_allowance,
            0,
        )

        return (
            income_tax
            + child_support_expense
            + childcare_expenses
            + additional_health_care_expenses
        )
