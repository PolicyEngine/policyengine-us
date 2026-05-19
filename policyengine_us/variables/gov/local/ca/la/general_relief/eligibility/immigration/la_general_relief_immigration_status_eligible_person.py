from policyengine_us.model_api import *


class la_general_relief_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible Person for the Los Angeles County General Relief based on the immigration status requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FGR%2FGR%2F42-404_Immigrant_Eligibility_Chart%2F42-404_Immigrant_Eligibility_Chart.htm"

    def formula(person, period, parameters):
        # Undocumented, DACA, and TPS classified applicants/participants are ineligible for GR
        istatus = person("immigration_status", period)
        daca = istatus == istatus.possible_values.DACA
        tps = istatus == istatus.possible_values.TPS
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Assuming that the applicant's/participant's immigration status is recorded
        return ~(daca | tps | undocumented) & head_or_spouse
