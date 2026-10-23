from policyengine_us.model_api import *


class al_other_federal_payment_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Other federal payment credits reducing Alabama's federal tax deduction"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.AL
    documentation = (
        "Actual federal payment credits not already included by the named "
        "Alabama federal-tax-deduction credit variables. Excludes withholding, "
        "estimated tax payments, extension payments, and amounts excluded by "
        "Act 2021-1, section 2(b), including recovery rebate credits."
    )
    reference = (
        "https://www.revenue.alabama.gov/wp-content/uploads/2021/12/810-3-15-.20.pdf#page=2",
        # Act 2021-1 (HB 170), section 2(b).
        "https://alison.legislature.state.al.us/files/pdf/SearchableInstruments/2021RS/PrintFiles/HB170-Enr.pdf#page=3",
    )
