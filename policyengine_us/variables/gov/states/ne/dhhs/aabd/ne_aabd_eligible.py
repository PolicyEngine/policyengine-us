from policyengine_us.model_api import *


class ne_aabd_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Nebraska Aid to the Aged, Blind, or Disabled"
    definition_period = MONTH
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Documents/Title-469-Complete.pdf#page=126",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ne.pdf#page=1",
    )

    def formula(person, period):
        # Per 469 NAC 3-006.01A1, AABD-PMT requires the person to be an
        # SSI recipient. ssi > 0 already implies categorical (aged/blind/
        # disabled), resource, immigration eligibility, the federal
        # income test, and takeup -- so no separate is_ssi_eligible
        # check is needed.
        return (person("ssi", period) > 0) | person("receives_ssi", period)
