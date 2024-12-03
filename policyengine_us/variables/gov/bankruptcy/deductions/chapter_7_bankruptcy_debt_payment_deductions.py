from policyengine_us.model_api import *


class chapter_7_bankruptcy_debt_payment_deductions(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Debt payment deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=7"

    def formula(spm_unit, period, parameters):
        # seems to be redudent to the calculation process as we already have local standard deduction in line 9 line 13.