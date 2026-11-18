from policyengine_us.model_api import *


class wi_ssp_institutional_continuation(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin SSP temporary institutional continuation"
    documentation = "State payment remains authorized during a temporary institutional stay. The continuation ends with the first month following the 90th day in a nursing home."
    definition_period = MONTH
    reference = "https://www.emhandbooks.wisconsin.gov/ssi-admin/2/2.1_federal_and_state_ssi_recipients.htm"
