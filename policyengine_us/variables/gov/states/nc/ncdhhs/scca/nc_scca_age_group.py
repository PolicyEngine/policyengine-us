from policyengine_us.model_api import *


class nc_scca_age_group(Variable):
    value_type = int
    entity = Person
    label = "North Carolina SCCA age group"
    definition_period = YEAR
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/M/Market_Rates_Centers_Eff_10-1.pdf?ver=9w52alSPhmrmo0N9gGVMEw%3d%3d"

    def formula(person, period, parameters):
        """
        Returns the age group for NC SCCA:
        1 - Infant (0 to <1)
        2 - Toddler (1 to <3)
        3 - Preschooler (3 to <6)

        The school age group is hardcoded as 4 (one more than the maximum value in the parameter)
        """
        age = person("age", period)
        is_school_age = person("nc_scca_is_school_age", period)
        p = parameters(period).gov.states.nc.ncdhhs.scca

        # School age group is 4 (one more than the maximum value in the age.group parameter)
        SCHOOL_AGE_GROUP = 4

        # Use standard calculation for non-school age, SCHOOL_AGE_GROUP for school age
        return where(is_school_age, SCHOOL_AGE_GROUP, p.age.group.calc(age))
