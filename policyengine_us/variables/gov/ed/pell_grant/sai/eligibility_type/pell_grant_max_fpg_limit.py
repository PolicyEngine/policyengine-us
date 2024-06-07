from policyengine_us.model_api import *


class pell_grant_max_fpg_percent_limit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "The maximum FPG percent to qualify for the maximum Pell Grant"

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        joint = person.tax_unit("tax_unit_is_joint", period)

        p = parameters(period).gov.ed.pell_grant.sai.max_pell_limits

        return select(
            [dependent & ~joint, dependent & joint, ~dependent & ~joint, ~dependent & joint],
            [
                p.DEPENDENT_SINGLE,
                p.DEPENDENT_NOT_SINGLE,
                p.INDEPENDENT_SINGLE,
                p.INDEPENDENT_NOT_SINGLE,
            ],
        )
