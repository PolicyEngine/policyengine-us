from policyengine_us.model_api import *


class co_oap_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado Old Age Pension gross unearned income other than SSI"
    unit = USD
    definition_period = YEAR
    # PDF pages 68-72
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=68"

    def formula(person, period, parameters):
        sources = parameters(period).gov.states.co.ssa.oap.income.sources.unearned
        # 9 CCR 2503-5 3.520.785(B)(20): rental income counts "to the extent
        # it exceeds allowable expenses", so a loss does not offset other
        # income. No source counts below zero.
        return sum(max_(0, person(source, period)) for source in sources)
