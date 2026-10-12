from policyengine_us.model_api import *


class ma_ccfa_informal_child_care_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) informal child care reimbursement amount per child"
    unit = USD
    reference = (
        "https://www.mass.gov/doc/eecfy26-rate-increase-rate-chart/download#page=2",
        "https://www.mass.gov/doc/fy26-motion-to-approve-fy27-rate-increases-to-informal-child-care-rates/download",
    )
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.eec.ccfa.reimbursement_rates.informal_child_care
        is_relative_home_care = person("ma_ccfa_is_in_relatives_home_care", period)
        return where(is_relative_home_care, p.relative_home, p.child_home)
