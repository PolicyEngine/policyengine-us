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
        "an eligibility-gated gross value before netting household-paid "
        "premiums; it is not enrollment- or take-up-gated. For 2024 "
        "simulations, net spending, enrollment, and cost-sharing offsets all "
        "use FY2024 calibration data."
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
