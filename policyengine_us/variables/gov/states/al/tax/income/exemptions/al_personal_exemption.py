from policyengine_us.model_api import *


class al_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama personal exemption"
    unit = USD
    # The Code of Alabama 1975 Section 40-18-19 (a)(8).
    documentation = "https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm"
    definition_period = YEAR
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions
        filing_status = tax_unit("filing_status", period)
        return p.personal[filing_status]
