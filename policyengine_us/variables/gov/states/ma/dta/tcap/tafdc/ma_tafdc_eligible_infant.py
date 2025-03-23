from policyengine_us.model_api import *


class ma_tafdc_eligible_infant(Variable):
    value_type = bool
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) eligible infant"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-705-600"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        # Monthly age is used to determine the age of the infant
        age = person("monthly_age", period)
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.tafdc.eligibility.age_limit
        return age < p.infant
