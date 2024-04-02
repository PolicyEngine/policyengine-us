from policyengine_us.model_api import *


class mi_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan personal and stillborn exemptions"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.exemptions

        # Personal Exemptions & Stillborn Exemptions
        exemptions = add(
            tax_unit, period, ["tax_unit_size", "tax_unit_stillborn_children"]
        )
        return exemptions * p.personal
