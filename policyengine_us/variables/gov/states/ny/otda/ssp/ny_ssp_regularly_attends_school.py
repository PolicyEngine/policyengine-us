from policyengine_us.model_api import *


class ny_ssp_regularly_attends_school(Variable):
    value_type = bool
    entity = Person
    label = "Regularly attends school for New York SSP"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-2.1",
        "https://www.law.cornell.edu/cfr/text/20/416.1861",
    )
    # Regular attendance under 20 CFR 416.1861, including qualifying part-time college
    # attendance (normally at least eight hours weekly), school or vocational training
    # and permitted reduced attendance or temporary absence. Full-time enrollment is the
    # fallback. Supply the actual attendance determination for other students; the
    # generic half-time college flag does not establish the required hours.

    def formula(person, period, parameters):
        return person("is_full_time_student", period)
