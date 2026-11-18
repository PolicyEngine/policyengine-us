from policyengine_us.model_api import *


class co_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Colorado State Supplement"
    unit = USD
    definition_period = MONTH
    defined_for = "co_state_supplement_eligible"
    reference = (
        # PDF pages 64, 91-96
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=64",
    )

    def formula(person, period, parameters):
        income = person("co_state_supplement_countable_income", period)
        ssi = person("ssi", period)
        total_countable_income = ssi + income
        p = parameters(period).gov.states.co.ssa.state_supplement
        # 9 CCR 2503-5 3.548(B), 3.549(B): the grant is the standard less
        # total countable income, SSI included.
        grant = max_(0, p.grant_standard - total_countable_income)
        # 3.520.781(A): a client whose total countable income equals or
        # exceeds the grant standard is not eligible. Since 2012 the standard
        # has equaled the SSI benefit standard for an individual, so this
        # also excludes those "receiving the full SSI benefit standard"
        # (3.546). A single client whose 3.549(A) income equals SSI's
        # countable income has SSI plus that income exactly at the standard,
        # so the test is on the grant in cents: single-precision arithmetic
        # must not turn a $0 grant into a positive one.
        eligible = np.round(grant, 2) > 0
        # 3.546(C)(2), (E), 3.549(B): an eligible client's grant below the
        # payment floor standard is raised to it by a state supplementary
        # payment.
        return where(eligible, max_(grant, p.payment_floor), 0)
