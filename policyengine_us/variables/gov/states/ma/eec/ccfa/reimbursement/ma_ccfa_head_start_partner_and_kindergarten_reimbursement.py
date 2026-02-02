from policyengine_us.model_api import *


class ma_ccfa_head_start_partner_and_kindergarten_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) head start partner and kindergarten reimbursement amount per child"
    unit = USD
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.reimbursement_rates
        region = person.household("ma_ccfa_region", period)
        schedule_type = person("ma_ccfa_schedule_type", period)
        return p.head_start_partner_and_kindergarten[region][schedule_type]
