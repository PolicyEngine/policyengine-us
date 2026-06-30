from policyengine_us.model_api import *


class per_capita_chip(Variable):
    value_type = float
    entity = Person
    label = "Average CHIP payment"
    unit = USD
    documentation = (
        "Per-capita separate CHIP payment for this person's State. "
        "PolicyEngine models Medicaid expansion CHIP children through "
        "Medicaid, so this uses separate CHIP spending and enrollment."
    )
    definition_period = YEAR
    reference = "https://www.macpac.gov/publication/chip-spending-by-state/"
    defined_for = "is_chip_eligible"

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        p = parameters(period).calibration.gov.hhs.cms.chip

        spending = p.spending.separate_chip.total[state_code]
        enrollment = p.enrollment.separate_chip[state_code]

        per_capita = np.zeros_like(enrollment, dtype=float)
        mask = enrollment > 0
        per_capita[mask] = spending[mask] / enrollment[mask]
        return per_capita
