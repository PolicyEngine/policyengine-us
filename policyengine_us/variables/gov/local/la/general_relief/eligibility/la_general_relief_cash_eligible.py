from policyengine_us.model_api import *


class la_general_relief_cash_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Los Angeles County General Relief based on the cash requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        cash = spm_unit("spm_unit_cash_assets", period)
        filing_status = spm_unit.tax_unit("filing_status", period)
        p = parameters(period).gov.local.la.general_relief.eligibility.limit
        return cash <= p.cash[filing_status]
