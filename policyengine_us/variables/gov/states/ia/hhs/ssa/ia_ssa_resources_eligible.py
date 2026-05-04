from policyengine_us.model_api import *


class ia_ssa_resources_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA resources eligible"
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.51.pdf#page=2"
    )

    def formula(person, period, parameters):
        # IAC 441—51.5(2): the recipient resource limit is $2,000 alone or
        # with a dependent child/parent only; $3,000 when there is a
        # dependent spouse, or with a spouse and a dependent child/parent.
        # Per 51.5(4) a dependent spouse can be an ineligible-but-financially-
        # dependent spouse. Apply the $3,000 marital-unit limit whenever the
        # recipient lives with any spouse — federal joint SSI claim is too
        # narrow because it requires both spouses to be SSI-categorically
        # eligible.
        individual_resources = person("ssi_countable_resources", period.this_year)
        marital_resources = person.marital_unit.sum(individual_resources)
        has_spouse = person.marital_unit.nb_persons() > 1
        resources_to_check = where(has_spouse, marital_resources, individual_resources)
        p = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        limit = where(has_spouse, p.couple, p.individual)
        return resources_to_check <= limit
