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
        age = person("age", period)
        
        # Hardcode calculation due to parameter validation issues
        # Will convert back to parameter-based when issue #5641 is fixed
        return select(
            [
                age < 1,
                age < 3,
                age < 6,
                age >= 6,
            ],
            [1, 2, 3, 4],
            default=0,
        )
