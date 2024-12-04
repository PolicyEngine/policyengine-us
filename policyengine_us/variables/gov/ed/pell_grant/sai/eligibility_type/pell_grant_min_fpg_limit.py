from policyengine_us.model_api import *


class pell_grant_min_fpg_percent_limit(Variable):
    value_type = float
    unit = "/1"
    entity = Person
    definition_period = YEAR
    label = "The maximum FPG percent to qualify for the minimum Pell Grant"

    def formula(person, period, parameters):
        household_type = person("pell_grant_household_type", period)
        limits = parameters(
            period
        ).gov.ed.pell_grant.sai.fpg_fraction.min_pell_limits
        not_parent = person.tax_unit("tax_unit_child_dependents", period) == 0

        independent = (
            household_type == household_type.possible_values.INDEPENDENT_SINGLE
        ) | (
            household_type
            == household_type.possible_values.INDEPENDENT_NOT_SINGLE
        )

        independent_parent = independent & not_parent

        return where(
            independent_parent,
            limits.INDEPENDENT_NOT_PARENT,
            limits[household_type],
        )
