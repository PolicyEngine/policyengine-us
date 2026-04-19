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
        "before netting their household-paid premium. Data years are not "
        "perfectly aligned: the net spending calibration is FY2023, "
        "enrollment is FY2022, and cost-sharing offsets are FY2024 "
        "(the most recent complete CMS-21 data). A follow-up will roll all "
        "three to the same fiscal year."
    )
    definition_period = YEAR
    reference = (
        "https://www.macpac.gov/publication/chip-spending-by-state/",
        "https://www.medicaid.gov/medicaid/financial-management/state-expenditure-reporting-for-medicaid-chip/expenditure-reports-mbescbes",
    )
    defined_for = "is_chip_eligible"

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        p = parameters(period).calibration.gov.hhs.cms.chip

        net_spending = p.spending.total.total[state_code]
        offsets = p.cost_sharing_offsets.total[state_code]
        gross_spending = net_spending + offsets
        enrollment = p.enrollment.total[state_code]

        per_capita = np.zeros_like(enrollment, dtype=float)
        mask = enrollment > 0
        per_capita[mask] = gross_spending[mask] / enrollment[mask]
        return per_capita
