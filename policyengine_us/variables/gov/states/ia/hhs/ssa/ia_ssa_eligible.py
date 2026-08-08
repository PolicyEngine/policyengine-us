from policyengine_us.model_api import *


class ia_ssa_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA eligible"
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/code/249.3.pdf",
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.51.pdf",
    )

    def formula(person, period, parameters):
        # Use SSI's categorical eligibility (aged/blind/disabled +
        # immigration) but apply Iowa's own resource test (IAC 441—51.5)
        # rather than the federal SSI resource test. Federal applies the
        # $2,000 individual limit when the spouse is not part of a joint
        # SSI claim, which would block Iowa's $3,000 marital-unit limit
        # for cases like a claimant with a non-ABD spouse and $2,500 in
        # combined resources. IAC 441—51.1 lets Iowa SSA pay recipients
        # who would qualify for SSI except for excess income, so the
        # federal resource test should not gate Iowa eligibility.
        abd = person("is_ssi_aged_blind_disabled", period.this_year)
        is_qualified_noncitizen = person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        immigration_status = person("immigration_status", period.this_year)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        meets_immigration = is_qualified_noncitizen | is_citizen
        resources_eligible = person("ia_ssa_resources_eligible", period)
        return abd & meets_immigration & resources_eligible
