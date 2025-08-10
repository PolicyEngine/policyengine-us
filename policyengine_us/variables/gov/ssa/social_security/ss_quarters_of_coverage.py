from policyengine_us.model_api import *


class ss_quarters_of_coverage(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    label = "Social Security quarters of coverage"
    documentation = (
        "Number of quarters of coverage earned in the year (maximum 4)"
    )
    reference = (
        "https://www.ssa.gov/OACT/COLA/QC.html",
        "https://www.law.cornell.edu/uscode/text/42/413",
    )

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)

        total_earnings = employment_income + self_employment_income

        p = parameters(period).gov.ssa.social_security

        # Calculate quarters earned (maximum 4 per year)
        quarters = np.floor(
            total_earnings / p.quarters_of_coverage_threshold
        ).astype(int)

        return min_(quarters, 4)
