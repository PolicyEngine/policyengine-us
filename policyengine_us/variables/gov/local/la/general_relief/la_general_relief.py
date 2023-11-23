from policyengine_us.model_api import *


class la_general_relief(Variable):
    value_type = float
    entity = SPMUnit
    label = "Los Angeles County General Relief"
    definition_period = MONTH
    defined_for = "la_general_relief_eligible"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        filing_status = spm_unit.tax_unit("filing_status", period)
        p = parameters(period).gov.local.la.general_relief
        return p.amount[filing_status]
