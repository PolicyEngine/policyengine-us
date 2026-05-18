from policyengine_us.model_api import *


class ak_months_since_atap_exit(Variable):
    value_type = int
    entity = SPMUnit
    label = "Months since Alaska Temporary Assistance Program (ATAP) case closed"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=1077"
