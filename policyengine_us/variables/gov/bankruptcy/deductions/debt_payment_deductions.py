from policyengine_us.model_api import *


class debt_payment_deductions(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Debt payment deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=7"
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
