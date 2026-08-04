from policyengine_us.model_api import *


class ca_marin_general_relief_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible applicant for the Marin County General Relief"
    definition_period = MONTH
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=12"

    def formula(person, period, parameters):
        immigration_eligible = person(
            "ca_marin_general_relief_immigration_status_eligible_person", period
        )
        # Standards Sec II.I bars the individual recipient ("An
        # Applicant/Recipient receiving SSI/SSP is not eligible for General
        # Relief") -- person-scoped like the fleeing-felon and probation bars,
        # so other members of the unit remain aidable. `ssi > 0` already
        # implies SSI receipt. CAPI (California's SSI-equivalent cash for
        # immigrants) needs no separate bar: CAPI recipients are non-qualified
        # noncitizens who fail the immigration check.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        return immigration_eligible & ~receives_ssi
