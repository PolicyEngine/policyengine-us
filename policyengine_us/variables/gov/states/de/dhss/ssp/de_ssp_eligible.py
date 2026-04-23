from policyengine_us.model_api import *


class de_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Delaware State Supplementary Payment"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415058",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/de.html",
    )

    def formula(person, period, parameters):
        # Delaware's SSP is federally administered; POMS SI 01415.058
        # is the authoritative source for eligibility and payment
        # levels. Income overspill is handled in de_ssp via the
        # uncapped_ssi reduction formula, so is_ssi_eligible is used
        # without an uncapped_ssi > 0 gate.
        is_ssi_eligible = person("is_ssi_eligible", period.this_year)
        is_adult = person("is_adult", period.this_year)
        living_arrangement = person.household("de_ssp_living_arrangement", period)
        in_certified_residential_care_home = (
            living_arrangement
            == living_arrangement.possible_values.CERTIFIED_RESIDENTIAL_CARE_HOME
        )
        return is_ssi_eligible & is_adult & in_certified_residential_care_home
