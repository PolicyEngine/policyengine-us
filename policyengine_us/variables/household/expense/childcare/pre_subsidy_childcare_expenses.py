from policyengine_us.model_api import *


class pre_subsidy_childcare_expenses(Variable):
    value_type = float
    entity = Person
    label = "Pre subsidy child care expenses"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        # distribute the SPM unit's childcare expenses evenly across
        # children in SPM unit's Tax units
        spm_unit = person.spm_unit
        childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        is_child = person("is_child", period)
        spm_unit_count_children = add(spm_unit, period, ["is_child"])
        # avoid array divide-by-zero warning by not using where() function
        # see the following GitHub issue for more details:
        # https://github.com/PolicyEngine/policyengine-us/issues/2494
        prorated_expenses = np.zeros_like(spm_unit_count_children)
        mask = spm_unit_count_children > 0
        prorated_expenses[mask] = (
            childcare_expenses[mask] / spm_unit_count_children[mask]
        )
        return prorated_expenses * is_child
