from policyengine_us.model_api import *


class il_hbi_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Illinois HBI resource eligibility"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = ("https://www.dhs.state.il.us/page.aspx?item=161600",)
    # Illinois HBIS (Health Benefits for Immigrant Seniors) has a resource limit
    # of $17,500 or less in non-exempt resources per household.
    #
    # This resource test only applies to seniors (age 65+) in the HBIS program.
    # Children (All Kids) and adults (HBIA) do not have a resource test.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbi.eligibility

        age = person("age", period)
        is_senior = age >= p.senior.min_age

        # Get household assets
        household_assets = person.spm_unit("spm_unit_assets", period)

        # Seniors must meet the resource test
        # Non-seniors automatically pass (no resource test)
        return where(
            is_senior,
            household_assets <= p.senior.resource_limit,
            True,
        )
