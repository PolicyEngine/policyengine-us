from policyengine_us.model_api import *


class s770_passive_se_income(Variable):
    value_type = float
    entity = Person
    label = "Intersection of passive and already SE covered entity income"
    documentation = "Intersection already included in both passive_partnership_s_corp_income and partnership_self_employment_net_earnings. Default zero assumes disjoint subsets; supply the validated intersection when they overlap. Active inclusion removes it from NII and subtracts only the active portion of already-SE income from the active residual."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
