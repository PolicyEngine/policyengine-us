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
        1 - Infant (0 to <=1)
        2 - Toddler (1 to <3)
        3 - Preschooler (3 to <6)
        4 - School age (6+)
        """

        p = parameters(period).gov.states.nc.ncdhhs.scca
        age = person("age", period)
        is_disabled_age = person(
            "nc_scca_is_eligible_disabled_age", period
        )  # disabled & < 18

        # Make sure 1 year old child in Group 1
        adjusted_age = where(age == 1, 0.99, age)

        # Assign age groups for children under 13, defaulting to school-age group for older children
        age_group = where(
            age < p.age.limit.non_disabled,
            p.age.group.calc(adjusted_age),
            p.age.group.calc(6),
        )

        # Override for disabled children who are above school age
        return where(is_disabled_age, p.age.group.calc(6), age_group)
