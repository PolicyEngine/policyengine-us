from policyengine_us.model_api import *


class ct_ceap_household_member(Variable):
    value_type = bool
    entity = Person
    label = "Connecticut CEAP household member"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=5"

    def formula(person, period, parameters):
        # Households exclude incarcerated people and foster children or adults.
        # January status stands in for status at application. Boarders and
        # residents of institutions of higher learning have no input.
        month = period.first_month
        return ~person("is_in_foster_care", month) & ~person("is_incarcerated", month)
