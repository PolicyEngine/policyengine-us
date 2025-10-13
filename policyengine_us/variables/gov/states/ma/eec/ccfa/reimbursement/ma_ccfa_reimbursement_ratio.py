from policyengine_us.model_api import *


class ma_ccfa_reimbursement_ratio(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) reimbursement ratio"
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.reimbursement_rates
        childcare_hours_per_day = person(
            "childcare_hours_per_day", period.this_year
        )
        return p.amount_ratio.calc(childcare_hours_per_day)
