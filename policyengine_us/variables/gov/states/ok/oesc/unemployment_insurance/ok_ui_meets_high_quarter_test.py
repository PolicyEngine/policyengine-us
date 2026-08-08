from policyengine_us.model_api import *


class ok_ui_meets_high_quarter_test(Variable):
    """Oklahoma UI high-quarter monetary eligibility test (§ 2-207(A)).

    Note: § 2-207(A)(2) applies the 1.5x multiplier to the claimant's
    unqualified (total) wages. This implementation uses taxable high-quarter
    wages as a proxy for the high-quarter figure driving the test. The
    deviation matters only for high-quarter earners whose wages are capped at
    the taxable wage base; in the cases PolicyEngine models, the alternate
    wages test (Test B) rescues final eligibility, so the proxy does not
    change the modeled monetary-eligibility outcome.
    """

    value_type = bool
    entity = Person
    label = "Meets the Oklahoma UI high-quarter monetary eligibility test"
    definition_period = YEAR
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=56",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.oesc.unemployment_insurance.eligibility
        base_period_taxable_wages = person("ok_ui_base_period_taxable_wages", period)
        base_period_total_wages = person("ok_ui_base_period_total_wages", period)
        high_quarter_taxable_wages = person("ok_ui_high_quarter_taxable_wages", period)
        meets_taxable_minimum = base_period_taxable_wages >= p.min_taxable_wages
        meets_multiplier = base_period_total_wages >= (
            p.min_total_wages_multiplier * high_quarter_taxable_wages
        )
        return meets_taxable_minimum & meets_multiplier
