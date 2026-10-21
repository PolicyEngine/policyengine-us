from policyengine_us.model_api import *


class per_capita_chip(Variable):
    value_type = float
    entity = Person
    label = "Average CHIP payment"
    unit = USD
    documentation = (
        "Per-capita separate CHIP payment for this person's State. "
        "PolicyEngine models Medicaid expansion CHIP children through "
        "Medicaid, so this uses separate CHIP spending and enrollment. "
        "From model year 2026, California CCHIP children instead use the "
        "DHCS Title 21 child cost estimate as a coverage-value proxy."
    )
    definition_period = YEAR
    reference = (
        "https://www.macpac.gov/publication/chip-spending-by-state/",
        # PDF pages 66,106: DHCS annual cost per eligible.
        "https://www.dhcs.ca.gov/hm/wp-content/uploads/2026/05/N25-Medi-Cal-Local-Assistance-Estimate.pdf#page=66",
    )
    defined_for = "is_chip_eligible"

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        p = parameters(period).calibration.gov.hhs.cms.chip

        spending = max_(p.spending.separate_chip.total[state_code], 0)
        enrollment = p.enrollment.separate_chip[state_code]

        per_capita = np.zeros_like(enrollment, dtype=float)
        mask = enrollment > 0
        per_capita[mask] = spending[mask] / enrollment[mask]
        return per_capita

    def formula_2026_01_01(person, period, parameters):
        per_capita = per_capita_chip.formula(person, period, parameters)
        state_code = person.household("state_code", period)
        category = person("chip_category", period)
        is_cchip = (state_code == StateCode.CA) & (
            category == category.possible_values.CHILD_CCHIP
        )
        p = parameters(period).gov.states.ca.dhcs.cchip
        return where(is_cchip, p.benefit_amount, per_capita)
