from policyengine_us.model_api import *


class co_ccap_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for Colorado Child Care Assistance Program"
    reference = (
        "https://docs.google.com/spreadsheets/d/1EEc3z8Iwu_KRTlBtd2NssDDEx_FITqVq/edit#gid=468321263",
        "https://docs.google.com/spreadsheets/d/1HtPiC2qxclzWfBa7LRo2Uohrg-RCBkyZ/edit#gid=582762342",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=17",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=31",
    )
    definition_period = YEAR
    defined_for = StateCode.CO
    
    def formula(tax_unit, period, parameters):
        is_entry = tax_unit("co_ccap_is_in_the_entry_process", period)
        entry_eligible = tax_unit("co_ccap_entry_eligible", period)
        is_re_determination = tax_unit("co_ccap_is_in_the_re_determination_process", period)
        re_determination_eligible = tax_unit(
            "co_ccap_re_determination_eligible", period
        )
        return (is_entry * entry_eligible) | (is_re_determination * re_determination_eligible)