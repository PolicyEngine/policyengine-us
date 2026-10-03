from policyengine_us.model_api import *


class ia_ssa_resources_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA resources eligible"
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.50.pdf",
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.51.pdf#page=2",
        "https://secure.ssa.gov/poms.nsf/lnx/0501110003",
        "https://secure.ssa.gov/poms.nsf/lnx/0501110530",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-416/subpart-K#p-416.1202(a)",
    )

    def formula(person, period, parameters):
        # IA SSA adopts the federal SSI $2,000 / $3,000 resource schedule
        # under the umbrella authority of IAC 441—50.2 (resource policy
        # follows SSI rules unless explicitly modified). Federal SSI applies
        # the $3,000 limit to "an individual with a spouse" whether the
        # spouse is eligible or ineligible, when they live in the same
        # household: SSA POMS SI 01110.003 (limits) and SI 01110.530 (deeming
        # of ineligible spouse resources), 20 CFR §416.1202(a). IAC
        # 441—51.5(2) carries the same $2k/$3k schedule for the dependent-
        # relative configuration. Apply the couple limit whenever the
        # recipient lives with any spouse — using `ssi_claim_is_joint` is too
        # narrow because it requires both spouses to be SSI-categorically
        # eligible.
        individual_resources = person("ssi_countable_resources", period.this_year)
        marital_resources = person.marital_unit.sum(individual_resources)
        has_spouse = person.marital_unit.nb_persons() > 1
        resources_to_check = where(has_spouse, marital_resources, individual_resources)
        p = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        limit = where(has_spouse, p.couple, p.individual)
        return resources_to_check <= limit
