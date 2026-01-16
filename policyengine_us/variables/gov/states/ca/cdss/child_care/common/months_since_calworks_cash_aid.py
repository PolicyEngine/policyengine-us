from policyengine_us.model_api import *


class months_since_calworks_cash_aid(Variable):
    value_type = int
    entity = SPMUnit
    label = "Months since CalWORKs cash aid ended"
    definition_period = MONTH
    defined_for = StateCode.CA
    default_value = 0
    reference = "https://www.cdss.ca.gov/inforesources/calworks-child-care/program-eligibility"
