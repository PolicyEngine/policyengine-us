from policyengine_us.model_api import *


class id_tafi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho Temporary Assistance for Families in Idaho (TAFI)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.248"
    )
    defined_for = "id_tafi_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.tafi
        grant_standard = spm_unit("id_tafi_grant_standard", period)
        # Cap at maximum grant
        return min_(grant_standard, p.maximum_grant)
