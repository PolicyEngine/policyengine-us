from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ssa.oap._precision import cents


class co_oap_in_kind_support_and_maintenance(Variable):
    value_type = float
    entity = Person
    label = "Colorado Old Age Pension in-kind support and maintenance"
    unit = USD
    definition_period = MONTH
    # Not restricted to Colorado: co_oap_deemed_income reads it for a
    # client's spouse, who may live elsewhere (3.534(C)).
    # PDF pages 72-73
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=72"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.520.79: the ISM Colorado counts as unearned income,
        # SSA's matching ISM for an SSI recipient (3.520.79(B)(6),
        # 3.520.71(E)) and Colorado's own amount for others (3.520.79(C)).
        # Monthly amounts in cents (see _precision.py).
        return cents(person("co_ssa_in_kind_support_and_maintenance", period))
