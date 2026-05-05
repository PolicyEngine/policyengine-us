from policyengine_us.model_api import *


class ne_aabd(Variable):
    value_type = float
    entity = Person
    label = "Nebraska Aid to the Aged, Blind, or Disabled"
    unit = USD
    definition_period = MONTH
    defined_for = "ne_aabd_eligible"
    reference = (
        "https://dhhs.ne.gov/Documents/Title-469-Complete.pdf#page=126",
        "https://dhhs.ne.gov/Documents/469-000-211.pdf",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ne.pdf#page=1",
    )

    def formula(person, period):
        # Per 469 NAC 3-006.01A1, AABD-PMT fills the gap between the state
        # standard of need and the federal SSI benefit rate. NE's parameters
        # store the FULL standard of need (e.g., $1,236/mo for Assisted
        # Living 2021), so the formula subtracts the federal SSI rate to
        # arrive at the state supplement portion. income_excess captures
        # countable income above the FBR (rare for SSI recipients but
        # possible for joint-claim couples with deemed income).
        standard_of_need = person("ne_aabd_standard_of_need", period)
        federal_ssi = person("ssi_amount_if_eligible", period)
        uncapped_ssi = person("uncapped_ssi", period)
        income_excess = max_(0, -uncapped_ssi)
        return max_(0, standard_of_need - federal_ssi - income_excess)
