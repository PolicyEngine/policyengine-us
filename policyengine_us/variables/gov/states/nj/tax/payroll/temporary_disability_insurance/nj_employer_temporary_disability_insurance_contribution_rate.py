from policyengine_us.model_api import *

MONTHS_IN_QUARTER = 3


class nj_employer_temporary_disability_insurance_contribution_rate(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employer temporary disability insurance contribution rate"
    documentation = (
        "Annual new-employer rate of the New Jersey employer contribution to the "
        "State disability benefits fund. New Jersey assigns these rates for a "
        "July-June fiscal year, so the annual rate averages the rates in effect "
        "at the start of each calendar quarter, assuming wages accrue evenly "
        "over the year."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.NJ
    reference = (
        "https://www.nj.gov/labor/ea/employer-services/rate-info/",
        "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf#page=65",
    )

    def formula(person, period, parameters):
        quarter_starts = period.get_subperiods(MONTH)[::MONTHS_IN_QUARTER]
        return sum(
            parameters(
                quarter_start
            ).gov.states.nj.tax.payroll.temporary_disability_insurance.employer_rate
            for quarter_start in quarter_starts
        ) / len(quarter_starts)
