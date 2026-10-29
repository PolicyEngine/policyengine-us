from policyengine_us.model_api import *


class ssi_pmv_amount(Variable):
    value_type = float
    entity = Person
    label = "SSI presumed maximum value amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1140",
        "https://secure.ssa.gov/poms.nsf/lnx/0500835300",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320150",
    )

    def formula(person, period, parameters):
        # Sum completed monthly budgets; supplied amounts retain their annual basis.
        return person("ssi_pmv_amount_monthly", period)
