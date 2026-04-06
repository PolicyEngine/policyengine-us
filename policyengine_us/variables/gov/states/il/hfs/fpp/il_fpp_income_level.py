from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class il_fpp_income_level(Variable):
    value_type = float
    entity = Person
    label = "Illinois Family Planning Program income level"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=146077",
        "https://hfs.illinois.gov/medicalclients/familyplanning.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Only the applicant's income is counted (not household income)
        income = person("adjusted_gross_income_person", period)

        # Fixed household size of 2 per IL FPP policy
        p = parameters(period).gov.states.il.hfs.fpp.eligibility

        # Calculate FPG using fixed household size
        state_group = person.household("state_group_str", period)
        fpp_fpg = fpg(p.household_size, state_group, period, parameters)

        # Return income as fraction of FPL
        return income / fpp_fpg
