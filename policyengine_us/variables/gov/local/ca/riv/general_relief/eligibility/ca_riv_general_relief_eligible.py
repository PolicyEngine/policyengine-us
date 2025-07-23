from policyengine_us.model_api import *


class ca_riv_general_relief_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Riverside County General Relief"
    definition_period = MONTH
    defined_for = "in_riv"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.riv.general_relief
        # Age >= 18, or emancipated minor ?

        # citizen or eligible non-citizen
        # income eligible
        # asset eligible
        # meets work requirements
