from policyengine_us.model_api import *


class la_general_relief_immigration_status_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Los Angeles County General Relief based on the immigration status requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/gr/residence/immigrant-eligibility-chart.html"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_person = person(
            "la_general_relief_immigration_status_eligible_person", period
        )
        # To be eligible for General Relief (GR), at least one applicants/participants must
        # meet the eligibility criteria
        return spm_unit.any(eligible_person)
