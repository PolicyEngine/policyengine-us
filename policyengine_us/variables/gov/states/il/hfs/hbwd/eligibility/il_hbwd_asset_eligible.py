from policyengine_us.model_api import *


class il_hbwd_asset_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Illinois Health Benefits for Workers with Disabilities asset eligible"
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbwd.eligibility
        # Check countable assets against $25,000 limit
        countable_assets = person("il_hbwd_countable_assets", period)
        return countable_assets <= p.asset.limit
