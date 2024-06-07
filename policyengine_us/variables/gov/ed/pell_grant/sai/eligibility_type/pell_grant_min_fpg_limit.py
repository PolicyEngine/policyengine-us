from policyengine_us.model_api import *


class pell_grant_min_fpg_percent_limit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "The maximum FPG percent to qualify for the minimum Pell Grant"

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        joint = person.tax_unit("tax_unit_is_joint", period)
        not_parent = person.tax_unit("tax_unit_child_dependents", period) == 0

        p = parameters(period).gov.ed.pell_grant.sai.min_pell_limits

        return select(
            [
                dependent & ~joint,
                dependent & joint,
                ~dependent & not_parent,
                ~dependent & ~joint,
                ~dependent & joint,
            ],
            [
                p.DEPENDENT_SINGLE,
                p.DEPENDENT_NOT_SINGLE,
                p.INDEPENDENT_NOT_PARENT,
                p.INDEPENDENT_SINGLE,
                p.INDEPENDENT_NOT_SINGLE,
            ],
        )
