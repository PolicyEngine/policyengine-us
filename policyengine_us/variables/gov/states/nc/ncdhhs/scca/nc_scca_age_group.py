from policyengine_us.model_api import *


class nc_scca_age_group(Variable):
    value_type = int
    entity = Person
    label = "North Carolina SCCA age group"
    definition_period = YEAR
    reference = (
        "https://docs.google.com/spreadsheets/d/1y7p8qkiOrMAM42rtSwT_ZXeA5tzew4edNkrTXACxf4M/edit?gid=1339413807#gid=1339413807"
        "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/M/Market_Rates_Centers_Eff_10-1.pdf?ver=9w52alSPhmrmo0N9gGVMEw%3d%3d"
    )

    def formula(person, period, parameters):
        """
        Returns the age group for NC SCCA:
        1 - Infant (0 to <1)
        2 - Toddler (1 to <3)
        3 - Preschooler (3 to <6)
        4 - School age (6+)

        The school age group is dynamically determined as max(group parameter values) + 1
        """
        age = person("age", period)
        is_school_age = person("nc_scca_is_school_age", period)
        p = parameters(period).gov.states.nc.ncdhhs.scca

        # Get the maximum value from the age group parameter to determine school age group
        age_group_param = p.age.group
        brackets = age_group_param.brackets

        # Find the maximum value in the age group parameters
        max_group_value = max(bracket.amount for bracket in brackets)

        # School age group is the maximum group value plus 1 (should be 4)
        school_age_group = max_group_value + 1

        # Use standard calculation for non-school age, school_age_group for school age
        return where(is_school_age, school_age_group, p.age.group.calc(age))
