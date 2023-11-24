from policyengine_us.model_api import *


class la_general_relief_housing_subsidy_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for the Los Angeles County General Relief Housing Subsidy"
    )
    definition_period = YEAR
    # Person has to be a resident of LA County
    defined_for = "la_general_relief_eligible"
    reference = "https://dpss.lacounty.gov/en/cash/gr/housing.html"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        household = spm_unit.household
        # Person has to experience homelessness
        # Considering people who are about to loose housing as homeless
        homeless = household("is_homeless", period)
        # Person can be in a speicfic age range or disabled to be eligible
        age = person("age", period)
        p = parameters(period).gov.local.ca.la.general_relief.housing_subsidy
        age_eligible = p.age_eligibility.calc(age)
        # Assuming that disabled people are unable to work
        disabled = person("is_disabled", period)
        # Person or couple can not have dependents
        age_or_disability_eligible = spm_unit.any(age_eligible | disabled)
        dependents = add(spm_unit, period, ["tax_unit_dependents"])
        return age_or_disability_eligible & homeless & (dependents == 0)
