from policyengine_us.model_api import *


class nc_scca_is_school_age(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina SCCA school age determination"
    definition_period = YEAR
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        """
        Determines if a child is considered of school age for SCCA purposes.
        Children are considered school age if they are at or above the school age threshold.
        """
        age = person("age", period)
        p = parameters(period).gov.states.nc.ncdhhs.scca.age
        return age >= p.school
