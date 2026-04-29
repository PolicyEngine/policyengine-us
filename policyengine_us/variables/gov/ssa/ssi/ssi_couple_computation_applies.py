from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ssi_couple_computation_applies(Variable):
    value_type = bool
    entity = Person
    label = "SSI couple computation applies"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.414",
        "https://secure.ssa.gov/poms.nsf/lnx/0500501154",
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period)

        # 20 CFR 416.414(b)(2): Both in facility → couple computation
        # still applies ($60/month = $30 each).
        # 20 CFR 416.414(b)(3): One in facility → benefits computed
        # separately, each using their own countable income.
        # This variable intentionally does not change joint-claim status
        # or SSI spouse/individual classification. POMS SI 02005.050
        # turns on whether the facility separation is temporary or
        # permanent, and PolicyEngine does not currently model intent to
        # return. We therefore scope this variable to the benefit-
        # computation rule that 416.414(b) applies in either case.
        arrangement = person("ssi_federal_living_arrangement", period)
        in_facility = (
            arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        )
        one_in_facility = person.marital_unit.sum(in_facility) == 1

        return joint_claim & ~one_in_facility
