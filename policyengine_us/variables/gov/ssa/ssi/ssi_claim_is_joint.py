from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_eligible_apart_from_means,
    _ssi_spouse_index,
)


class ssi_claim_is_joint(Variable):
    value_type = bool
    entity = Person
    label = "SSI claim is joint"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1382c#b",
        "https://www.ecfr.gov/current/title-20/section-416.1801",
        "https://www.ecfr.gov/current/title-20/section-416.1802",
        "https://www.ecfr.gov/current/title-20/section-416.1806",
    )

    def formula(person, period, parameters):
        # 416.1801(c): an eligible spouse is eligible for SSI, is the spouse
        # of another person eligible for SSI, and lives in the same household
        # with that person. Spouses are found by the test resource deeming
        # uses (416.1806: husband or wife, living together), not by tax-unit
        # head and spouse roles, which go to the two oldest adults of a tax
        # unit when roles are not supplied. A spouse who fails the
        # citizenship condition is an ineligible spouse (416.1160(d)).
        eligible = _ssi_eligible_apart_from_means(person, period)
        spouse = _ssi_spouse_index(person, period)
        return eligible & (spouse >= 0) & eligible[np.maximum(spouse, 0)]
