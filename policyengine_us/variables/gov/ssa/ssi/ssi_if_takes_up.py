from policyengine_us.model_api import *


class ssi_if_takes_up(Variable):
    value_type = float
    entity = Person
    label = "SSI if takes up"
    documentation = (
        "Supplemental Security Income the person would receive if they "
        "take up the program, regardless of reported take-up."
    )
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/42/1382"

    def formula(person, period, parameters):
        if parameters(period).gov.ssa.ssi.abolish_ssi:
            return 0

        # Apply floor: SSI cannot be negative. Under spousal deeming,
        # uncapped_ssi already applies 20 CFR 416.1163(e)(2), which also keeps
        # the benefit at or below the individual Federal benefit rate.
        return max_(0, person("uncapped_ssi", period))
