from policyengine_us.model_api import *


class wy_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Wyoming State Supplemental Payment"
    definition_period = MONTH
    defined_for = StateCode.WY
    reference = (
        "https://ecom.wyo.gov/m1800-other-programs/m1804-state-supplemental-payments"
    )

    def formula(person, period, parameters):
        receives_ssi = person("ssi", period) > 0
        p = parameters(period).gov.ssa.ssi.income.sources
        # The sole-income rule precedes SSI exclusions. A loss in one source
        # cannot erase a positive payment from another source.
        sources = list(p.earned) + list(p.unearned)
        other_income = sum(max_(person(source, period), 0) for source in sources)
        return receives_ssi & (other_income == 0)
