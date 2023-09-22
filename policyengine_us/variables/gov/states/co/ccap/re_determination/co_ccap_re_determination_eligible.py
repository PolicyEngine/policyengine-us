from policyengine_us.model_api import *


class co_ccap_re_determination_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the re-determination of the Colorado Child Care Assistance Program"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=31",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        income_eligible = tax_unit("co_ccap_re_determination_income_eligible", period)
        child_age_eligible = (
            tax_unit("co_ccap_num_child_eligible", period) > 0
        )
        return income_eligible & child_age_eligible
