from policyengine_us.model_api import *


class ca_calworks_child_care_payment_standard(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Child Care Payment Standard"
    definition_period = YEAR
    defined_for = "is_child"
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.child_care.rate_ceilings
        provider = person("ca_calworks_child_care_provider_category", period)
        time = person("ca_calworks_child_care_time_category", period)
        service = person("ca_calworks_child_care_service_category", period)
        age = person("age", period)

        return select(
            [age < p.age_threshold.lower, age > p.age_threshold.higher],
            [
                p.standard.younger[provider][time][service],
                p.standard.older[provider][time][service],
            ],
            default=p.standard.middle[provider][time][service]
        )
