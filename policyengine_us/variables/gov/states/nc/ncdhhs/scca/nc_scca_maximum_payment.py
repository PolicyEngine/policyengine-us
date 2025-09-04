from policyengine_us.model_api import *


class nc_scca_maximum_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance Program maximum payment"
    unit = USD
    definition_period = MONTH
    reference = "https://www.publichealthlawcenter.org/sites/default/files/NC%20Chapter%2010%20Subsidized%20Child%20Care%20Rules.pdf#page=2"
    defined_for = "nc_scca_entry_eligible"

    def formula(spm_unit, period, parameters):
        total_market_rate = add(spm_unit, period, ["nc_scca_market_rate"])

        parent_fee = spm_unit("nc_scca_parent_fee", period)
        return max_(total_market_rate - parent_fee, 0)
