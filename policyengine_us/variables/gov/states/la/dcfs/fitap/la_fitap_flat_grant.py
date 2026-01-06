from policyengine_us.model_api import *


class la_fitap_flat_grant(Variable):
    value_type = float
    entity = SPMUnit
    label = "Louisiana FITAP flat grant"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://ldh.la.gov/page/fitap",
        "https://www.dcfs.louisiana.gov/news/louisiana-to-increase-tanf-cash-assistance-benefits-beginning-january-2022",
    )
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.dcfs.fitap.flat_grant
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, 10)
        return p.amount[capped_size]
