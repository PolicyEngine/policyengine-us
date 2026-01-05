from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


class mn_minnesotacare_group(Variable):
    """Maps MinnesotaCare eligibility to Medicaid spending groups.

    MinnesotaCare for undocumented children → CHILD
    """

    value_type = Enum
    possible_values = MedicaidGroup
    default_value = MedicaidGroup.NONE
    entity = Person
    label = "MinnesotaCare spending group"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = [
        "https://www.revisor.mn.gov/statutes/cite/256L.04",
    ]

    def formula(person, period, parameters):
        children_eligible = person(
            "mn_minnesotacare_children_eligible", period
        )

        return where(
            children_eligible,
            MedicaidGroup.CHILD,
            MedicaidGroup.NONE,
        )
