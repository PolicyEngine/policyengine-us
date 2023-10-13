from policyengine_us.model_api import *


class co_ccap_entry_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the entry of Colorado Child Care Assistance Program through income"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        hhs_fpg_eligible = tax_unit("co_ccap_hhs_fpg_eligible", period)
        hhs_smi_eligible = tax_unit("co_ccap_hhs_smi_eligible", period)
        return hhs_fpg_eligible & hhs_smi_eligible
