from policyengine_us.model_api import *


class ca_calworks_child_care_payment_standard(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Child Care Payment Standard"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_calworks_child_care_child_age_eligible"
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.child_care.rate_ceilings
        # Payment standard is the maximum payment depending on:
        # - Period (hourly/daily/weekly/monthly)
        # - Care facility type
        # - Full-time/part-time
        provider = person("ca_calworks_child_care_provider_category", period)
        time = person("ca_calworks_child_care_time_category", period)
        is_full_time = person("ca_calworks_child_care_full_time", period)
        age = person("age", period.this_year)

        age_group = select(
            [age < p.age_threshold.lower, age > p.age_threshold.higher],
            ["younger", "older"],
            default="middle",
        )
        return p.standard[age_group][provider][time][is_full_time]
