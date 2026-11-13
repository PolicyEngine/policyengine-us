from policyengine_us.model_api import *


class ssi_in_kind_support_and_maintenance(Variable):
    value_type = float
    entity = Person
    label = "SSI in-kind support and maintenance"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1130",
        "https://www.law.cornell.edu/cfr/text/20/416.1140",
    )

    def formula(person, period, parameters):
        # Sum completed monthly budgets; supplied amounts retain their annual basis.
        return person("ssi_in_kind_support_and_maintenance_monthly", period)
