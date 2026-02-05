from policyengine_us.model_api import *


class nj_unemployment_insurance_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for New Jersey unemployment insurance"
    documentation = "Indicates whether a person meets the monetary eligibility requirements for New Jersey unemployment insurance. Eligibility requires either: (1) 20+ base weeks with minimum weekly earnings, or (2) total base period earnings above the alternative threshold."
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/who/",
        "https://www.nj.gov/labor/lwdhome/press/2025/20251229_newbenefitrates2026.shtml",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        # Get inputs
        base_weeks = person(
            "nj_unemployment_insurance_base_period_weeks", period
        )
        base_wages = person(
            "nj_unemployment_insurance_base_period_wages", period
        )

        # Get parameters
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        min_weeks = p.min_base_weeks
        min_total_earnings = p.min_total_base_earnings

        # Check eligibility paths
        # Option 1: 20+ base weeks (base weeks already count only weeks meeting minimum earnings)
        meets_weeks_test = base_weeks >= min_weeks

        # Option 2: Alternative total earnings threshold
        meets_earnings_test = base_wages >= min_total_earnings

        return meets_weeks_test | meets_earnings_test
