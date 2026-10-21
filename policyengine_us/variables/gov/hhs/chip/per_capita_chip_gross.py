from policyengine_us.model_api import *


class per_capita_chip_gross(Variable):
    value_type = float
    entity = Person
    label = "Average gross CHIP benefit value"
    unit = USD
    documentation = (
        "Per-capita gross CHIP service value for this person's state, equal "
        "to the net federal-plus-state CHIP expenditure plus the household "
        "cost-sharing collections that offset it on CMS-21. This represents "
        "the gross benefit value a CHIP enrollee receives (the service), "
        "before netting their household-paid premium. For 2024 simulations, "
        "separate CHIP net spending, enrollment, and cost-sharing offsets "
        "all use FY2024 calibration data. From model year 2026, California "
        "CCHIP children instead use the DHCS Title 21 child cost estimate "
        "for both net and gross coverage values."
    )
    definition_period = YEAR
    reference = (
        "https://www.macpac.gov/publication/chip-spending-by-state/",
        "https://www.medicaid.gov/medicaid/financial-management/state-expenditure-reporting-for-medicaid-chip/expenditure-reports-mbescbes",
        # PDF pages 66,106: DHCS annual cost per eligible.
        "https://www.dhcs.ca.gov/hm/wp-content/uploads/2026/05/N25-Medi-Cal-Local-Assistance-Estimate.pdf#page=66",
    )
    defined_for = "is_chip_eligible"

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        p = parameters(period).calibration.gov.hhs.cms.chip

        net_spending = p.spending.separate_chip.total[state_code]
        offsets = p.cost_sharing_offsets.separate_chip[state_code]
        gross_spending = max_(net_spending + offsets, 0)
        enrollment = p.enrollment.separate_chip[state_code]

        per_capita = np.zeros_like(enrollment, dtype=float)
        mask = enrollment > 0
        per_capita[mask] = gross_spending[mask] / enrollment[mask]
        return per_capita

    def formula_2026_01_01(person, period, parameters):
        per_capita = per_capita_chip_gross.formula(person, period, parameters)
        state_code = person.household("state_code", period)
        category = person("chip_category", period)
        is_cchip = (state_code == StateCode.CA) & (
            category == category.possible_values.CHILD_CCHIP
        )
        p = parameters(period).gov.states.ca.dhcs.cchip
        return where(is_cchip, p.benefit_amount, per_capita)
