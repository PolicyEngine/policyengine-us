from policyengine_us.model_api import *


class ma_tafdc_work_related_expense_deduction(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) work-related expense deduction"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-270"
    )
    defined_for = StateCode.MA

    # adds = ["gov.states.ma.dta.tcap.deductions.work_related_expenses.amount"]
