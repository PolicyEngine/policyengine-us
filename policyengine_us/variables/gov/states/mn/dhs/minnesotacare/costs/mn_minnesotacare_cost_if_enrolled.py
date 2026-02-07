from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


class mn_minnesotacare_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Per capita MinnesotaCare cost by eligibility group"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = [
        "https://www.revisor.mn.gov/statutes/cite/256L.04",
    ]
    documentation = """
    Calculates the per-capita cost of MinnesotaCare coverage based on the
    person's eligibility group. Uses Minnesota state Medicaid cost data
    by eligibility category.

    Note: MinnesotaCare for undocumented children is 100% state-funded
    and delivered on a fee-for-service basis.
    """

    def formula(person, period, parameters):
        group = person("mn_minnesotacare_group", period)

        p = parameters(period).calibration.gov.hhs.medicaid

        is_child = group == MedicaidGroup.CHILD

        # Use Minnesota state Medicaid cost data
        child_spend = p.spending.by_eligibility_group.child["MN"]
        child_enroll = p.enrollment.child["MN"]

        spend = where(is_child, child_spend, 0)
        enroll = where(is_child, child_enroll, 0)

        # Calculate per-capita cost, avoiding divide-by-zero
        return np.where(enroll > 0, spend / enroll, 0)
