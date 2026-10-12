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

        uncapped = person("uncapped_ssi", period)

        # Apply floor: SSI cannot be negative
        benefit = max_(0, uncapped)

        # Apply cap when spousal deeming: cannot exceed individual FBR
        # per 20 CFR §416.1163
        # This cap is necessary when spouse's gross income is just above $483:
        # - Deeming applies (uses couple FBR)
        # - After exclusions, countable may be low
        # - Benefit could exceed individual FBR without this cap
        deeming_applies = person("is_ssi_spousal_deeming_applies", period.this_year)
        p = parameters(period).gov.ssa.ssi.amount
        capped_benefit = min_(benefit, p.individual)

        return where(
            deeming_applies,
            capped_benefit,
            benefit,
        )
