from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class is_ssi_ineligible_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible spouse"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1382c#b",
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(d)",
        "https://www.ecfr.gov/current/title-20/section-416.1806",
    )

    def formula(person, period, parameters):
        # 416.1160(d): 'Ineligible spouse means someone who lives with you as
        # your husband or wife and is not eligible for SSI benefits.' The
        # spouse test is the one joint claims and resource deeming use, so a
        # spouse who is not a tax-unit head or spouse still counts. Like
        # ssi_claim_is_joint, this tests aged, blind or disabled status only.
        abd = person("is_ssi_aged_blind_disabled", period)
        spouse = _ssi_spouse_index(person, period)
        return ~abd & (spouse >= 0) & abd[np.maximum(spouse, 0)]
