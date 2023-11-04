from policyengine_us.model_api import *


class la_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana personal exemption"
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=101761"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA
    adds = [
        "la_blind_exemption",
        "la_dependents_exemption",
        "la_widow_exemption",
        "la_aged_exemption",
    ]

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        personal_exemption = parameters(
            period
        ).gov.states.la.tax.income.exemptions.personal.personal[filing_status]
        personal_exemption += tax_unit("la_blind_exemption", period)
        personal_exemption += tax_unit("la_dependents_exemption", period)
        personal_exemption += tax_unit("la_widow_exemption", period)
        personal_exemption += tax_unit("la_aged_exemption", period)
        return personal_exemption
