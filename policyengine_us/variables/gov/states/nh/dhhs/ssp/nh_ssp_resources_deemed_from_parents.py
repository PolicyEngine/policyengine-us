from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed.ssi_resources_deemed_from_ineligible_parent import (
    _ssi_parental_resource_pool,
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
    # under He-W 601.06(b); the federal pool also counts a named parent's
    # co-resident spouse. Override with the agency-determined amount for a different
    # certified budget, temporary absence, or the month of the eighteenth birthday;
    # annual age cannot identify that month.

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        parental_resources, parent_count, _ = _ssi_parental_resource_pool(
            person, period, person("ssi_resources_for_deeming", period)
        )
        allowance = where(parent_count > 1, p.couple, p.individual)
        excess = max_(0, parental_resources - allowance)
        return (
            person("is_child", period.this_year)
            * person("is_blind", period.this_year)
            * excess
        )
