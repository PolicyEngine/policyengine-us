from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class is_ssi_spousal_resource_deeming_applies(Variable):
    value_type = bool
    entity = Person
    label = "Ineligible spouse's resources are deemed for SSI"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(a)",
        "https://www.ecfr.gov/current/title-20/section-416.1160",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330100",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
    )

    def formula(person, period, parameters):
        # 416.1160: an ineligible spouse 'lives with you as your husband or
        # wife and is not eligible for SSI benefits'. Identify the spouse with
        # the same evidence as a parent's spouse in parental deeming, so one
        # couple is never married for one rule and not the other. 416.1167
        # retains an absent person's household membership: enter a temporarily
        # absent spouse in the household they remain a member of.
        spouse = _ssi_spouse_index(person, period)
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        # As is_ssi_ineligible_spouse, a spouse who is not aged, blind or
        # disabled cannot be eligible; two such spouses claim jointly.
        spouse_ineligible = (spouse >= 0) & ~aged_blind_disabled[np.maximum(spouse, 0)]
        return (
            aged_blind_disabled
            & ~person("ssi_claim_is_joint", period)
            & spouse_ineligible
        )
