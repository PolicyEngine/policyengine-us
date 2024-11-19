from policyengine_us.model_api import *


class other_necessary_expenses_deductions(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Other necessary expenses deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=5"
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        taxes = add(spm_unit, period, ["income_tax"])
        ## retirement_contribution 
        child_support_expense = add(spm_unit, period, ["child_support_expense"])
        childcare_expenses = spm_unit("childcare_expenses", period)
        ## ???
        line_7 = spm_unit("line_7",period)
        out_of_pocket_healthcare_expense = add(spm_unit, period,["medical_out_of_pocket_expenses"])
        line_22 = out_of_pocket_healthcare_expense - line_7
        ##
        total = taxes + child_support_expense + childcare_expenses + line_22
        return total/MONTHS_IN_YEAR
