from policyengine_us.model_api import *


class ok_ssp_spouse_child_allocation(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma SSP ineligible spouse allocation for dependent children"
    definition_period = MONTH
    unit = USD
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-5"
    documentation = "Default uses the family's non-SSI children. Override with the verified allocation for blended families or children in a TANF case."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ssp
        child = person("is_ssi_ineligible_child", period.this_year)
        child_income = max_(person("ssi_earned_income", period), 0) + max_(
            person("ssi_unearned_income", period), 0
        )
        allocation = child * max_(p.child_allocation - child_income, 0)
        return person.family.sum(allocation)
