from policyengine_us.model_api import *


class mt_ssp_individual(Variable):
    value_type = float
    entity = Person
    label = "Montana SSP individual payment amount"
    unit = USD
    definition_period = MONTH
    defined_for = "mt_ssp_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-104",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN",
    )

    def formula(person, period, parameters):
        category = person("mt_ssp_payment_category", period)
        p = parameters(period).gov.states.mt.dphhs.ssp
        return p.amount.individual[category]
