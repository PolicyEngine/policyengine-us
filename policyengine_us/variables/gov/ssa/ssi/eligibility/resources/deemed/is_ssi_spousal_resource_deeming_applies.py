from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class is_ssi_spousal_resource_deeming_applies(Variable):
    value_type = bool
    entity = Person
    label = "Spouse's resources count toward the SSI resource test"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(a)",
        "https://www.ecfr.gov/current/title-20/section-416.1160",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330100",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
    )

    def formula(person, period, parameters):
        # 416.1160: an ineligible spouse 'lives with you as your husband or
        # wife and is not eligible for SSI benefits'; 416.1205(a) counts 'the
        # resources of the spouse' against the couple limit. Eligibility is
        # not known before the resource test, and 416.1205(b) tests an
        # eligible couple's combined resources against the same limit, so a
        # spouse's resources count either way when the claim is not already
        # joint. The spouse is identified as a parent's spouse is in parental
        # deeming. 416.1167 retains an absent person's household membership:
        # enter a temporarily absent spouse in the household they remain in.
        spouse = _ssi_spouse_index(person, period)
        return (
            person("is_ssi_aged_blind_disabled", period)
            & ~person("ssi_claim_is_joint", period)
            & (spouse >= 0)
        )
