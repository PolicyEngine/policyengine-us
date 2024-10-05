from policyengine_us.model_api import *


class ca_tanf_resources_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Resources Limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F42-200_Property%2F42-200_Property.htm%23Policybc-2&rhtocid=_3_1_2_0_1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.cash.resources.limit
        persons = spm_unit.members
        age = persons("age", period)
        has_elderly = spm_unit.any(age >= p.age_threshold)
        is_disabled = persons("is_disabled", period)
        has_disabled_member = spm_unit.any(is_disabled)
        return where(
            has_elderly | has_disabled_member,
            p.with_elderly_or_disabled_member,
            p.without_elderly_or_disabled_member,
        )
