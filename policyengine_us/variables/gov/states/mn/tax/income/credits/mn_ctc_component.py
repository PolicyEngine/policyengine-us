from policyengine_us.model_api import *


class mn_ctc_component(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Child Tax Credit component"
    unit = USD
    definition_period = YEAR
    reference = ("https://www.revisor.mn.gov/statutes/cite/290.0661",)
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # MN combines CTC and WFC into mn_child_and_working_families_credits.
        # The WFC portion is already in state_eitcs via mn_wfc.
        # This extracts just the CTC portion to avoid double-counting.
        combined = tax_unit("mn_child_and_working_families_credits", period)
        wfc = tax_unit("mn_wfc", period)
        return max_(0, combined - wfc)
