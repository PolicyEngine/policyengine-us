from policyengine_us.model_api import *


class pell_grant_max_fpg_percent_limit(Variable):
    value_type = float
    entity = Person
    unit = "/1"
    definition_period = YEAR
    label = "The maximum FPG percent to qualify for the maximum Pell Grant"

    def formula(person, period, parameters):
        household_type = person("pell_grant_household_type", period)
        limits = parameters(
            period
        ).gov.ed.pell_grant.sai.fpg_fraction.max_pell_limits

        return limits[household_type]
