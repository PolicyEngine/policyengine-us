from policyengine_us.model_api import *
from policyengine_us.tools.social_security_benefit_levers import SocialSecurityFund


class social_security_dependents_payable_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = "/1"
    label = "Social Security dependents payable factor"

    def formula(person, period, parameters):
        p = parameters(period).gov.contrib.ssa.benefit_levers.payable
        factor = person("social_security_payable_factor", period)
        if not p.oasi_only or np.all(factor == 1):
            return factor
        fund = person("social_security_dependents_fund", period)
        base = person("social_security_dependents_base", period)
        if np.any((base > 0) & (fund == SocialSecurityFund.unspecified)):
            raise ValueError(
                "OASI-only payable cuts require the dependent benefit fund"
            )
        return where(fund == SocialSecurityFund.oasi, factor, 1)
