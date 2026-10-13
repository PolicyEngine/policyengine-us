from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ssa.oap._precision import PRECISION


class co_oap(Variable):
    value_type = float
    entity = Person
    label = "Colorado Old Age Pension"
    unit = USD
    definition_period = YEAR
    defined_for = "co_oap_eligible"
    # PDF pages 64, 74-77, 134
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=64"

    def formula(person, period, parameters):
        total = 0
        for month in period.get_subperiods(MONTH):
            p = parameters(month).gov.states.co.ssa.oap
            # 9 CCR 2503-5 3.532(B), 3.533(B): the grant is the grant standard
            # less total countable income, SSI included (3.533(A)(2)(d)).
            ssi = person("ssi", month)
            income = ssi + person("co_oap_countable_income", month)
            grant = p.grant_standard - income
            # 3.533 and 3.520.781(A): a client whose total countable income
            # equals or exceeds the grant standard is not eligible.
            # 3.531(D)(2), 3.532(B), 3.533(B): an eligible client's grant below
            # the payment floor standard is raised to it by a state
            # supplementary payment, month by month.
            payment = where(grant > PRECISION, max_(grant, p.payment_floor), 0)
            # 3.581(E): payments drop any cents, "except in cases where SSI
            # income reduces the grant".
            payment = where(ssi > 0, payment, np.floor(payment + PRECISION))
            total = total + payment
        return total
