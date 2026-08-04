from policyengine_us.model_api import *


class ca_sf_caap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Francisco County CAAP countable cash income"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(spm_unit, period, parameters):
        # Cash income only. In-kind value is deducted from the grant in the
        # benefit formula (SEC. 20.7-22(c)), not the net-income eligibility test
        # (SEC. 20.7-10), and is protected by the $59 floor (SEC. 20.7-24).
        income = spm_unit.members("ca_sf_caap_countable_income_person", period)
        # Only count the income of persons in the budget unit. SSI recipients
        # (and persons without a qualified immigration status) are excluded from
        # CAAP, so their income is also excluded (SEC. 20.7-14).
        eligible = spm_unit.members("ca_sf_caap_eligible_person", period)
        return spm_unit.sum(where(eligible, income, 0))
