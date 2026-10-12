from policyengine_us.model_api import *
from policyengine_us.variables.gov.states._ssp_parental_resources import (
    ssp_parental_resources,
)


class nh_ssp_resources_deemed_from_parents(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire ANB resources deemed from parents"
    definition_period = MONTH
    quantity_type = STOCK
    unit = USD
    defined_for = StateCode.NH
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    # He-W 652.03(i)-(j) adds the co-resident parents' resources above the federal
    # one/two-parent allowance to a blind child's own resources. It does not divide that
    # excess between siblings. Parent includes a biological, adoptive or stepparent
    # under He-W 601.06(b). Override with the agency-determined amount for a different
    # certified budget, temporary absence, or the month of the eighteenth birthday;
    # annual age cannot identify that month.

    def formula(person, period, parameters):
        _, _, excess = ssp_parental_resources(person, period, parameters)
        return (
            person("is_child", period.this_year)
            * person("is_blind", period.this_year)
            * excess
        )
