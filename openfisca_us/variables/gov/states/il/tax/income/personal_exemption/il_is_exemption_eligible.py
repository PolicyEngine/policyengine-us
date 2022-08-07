from openfisca_us.model_api import *


class il_is_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether this tax unit is eligible for any exemptions"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.personal_exemption.cap
        filing_status = tax_unit("filing_status", period)
        joint = where(
            filing_status == filing_status.possible_values.JOINT,
            "joint",
            "nonjoint",
        )

        return tax_unit("adjusted_gross_income", period) < p[joint]
