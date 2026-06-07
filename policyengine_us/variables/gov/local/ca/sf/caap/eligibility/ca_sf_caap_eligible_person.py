from policyengine_us.model_api import *


class ca_sf_caap_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Counts toward the San Francisco County CAAP budget unit"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(person, period, parameters):
        # A person counts toward the CAAP budget unit only if they are not served
        # by an individual SSI-type cash program and have a qualified immigration
        # status (SEC. 20.7-6, 20.7-14). SSI recipients are served by SSI/SSP, and
        # aged/blind/disabled immigrants eligible for CAPI are served by CAPI;
        # both are individual programs, so the bar applies per person (SSIP, a
        # CAAP sub-program, serves SSI-pending applicants).
        receives_ssi = person("ssi", period) > 0
        capi_eligible = person("ca_capi_eligible_person", period.this_year)
        immigration_status_eligible = person(
            "ca_sf_caap_immigration_status_eligible", period
        )
        return ~receives_ssi & ~capi_eligible & immigration_status_eligible
