from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ia.hhs.cca.ia_cca_provider_type import (
    IACCAProviderType,
)


class ia_cca_max_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Iowa CCA maximum half-day-unit rate per child"
    definition_period = MONTH
    defined_for = "ia_cca_eligible_child"
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=14"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.payment
        provider_type = person("ia_cca_provider_type", period)
        quality_rating = person("ia_cca_quality_rating", period)
        age_group = person("ia_cca_age_group", period)

        licensed_center_rate = p.rates.licensed_center[quality_rating][age_group]
        child_dev_home_ab_rate = p.rates.child_dev_home_ab[quality_rating][age_group]
        child_dev_home_c_rate = p.rates.child_dev_home_c[quality_rating][age_group]
        not_registered_rate = p.rates.child_care_home_not_registered[age_group]

        # Iowa pays the in-home (Table 5) minimum-wage rate only when at
        # least three children in the family require care
        # (IAC 441-170.4(8)"d").
        children_in_care = person.spm_unit("ia_cca_children_in_care", period)
        in_home_allowed = children_in_care >= p.in_home_min_children
        in_home_rate = where(in_home_allowed, p.in_home_rate, 0)

        return select(
            [
                provider_type == IACCAProviderType.LICENSED_CENTER,
                provider_type == IACCAProviderType.CHILD_DEVELOPMENT_HOME_AB,
                provider_type == IACCAProviderType.CHILD_DEVELOPMENT_HOME_C,
                provider_type == IACCAProviderType.CHILD_CARE_HOME_NOT_REGISTERED,
                provider_type == IACCAProviderType.IN_HOME,
            ],
            [
                licensed_center_rate,
                child_dev_home_ab_rate,
                child_dev_home_c_rate,
                not_registered_rate,
                in_home_rate,
            ],
            default=licensed_center_rate,
        )
