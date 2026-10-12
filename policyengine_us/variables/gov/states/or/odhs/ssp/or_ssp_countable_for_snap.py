from policyengine_us.model_api import *


class or_ssp_countable_for_snap(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP included in SNAP unearned income"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://sharedsystems.dhsoha.state.or.us/DHSForms/Served/de2818.pdf#page=583",
    )
    documentation = "The OPEN manual identifies the in-home supplement as a reimbursement that does not affect other program benefits."

    def formula(person, period, parameters):
        category = person("or_ssp_category", period)
        reimbursement = category == category.possible_values.IN_HOME
        return where(reimbursement, 0, person("or_ssp", period))
