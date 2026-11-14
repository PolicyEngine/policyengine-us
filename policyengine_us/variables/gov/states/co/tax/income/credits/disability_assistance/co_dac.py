from policyengine_us.model_api import *


class co_dac(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Disability Assistance Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "co_dac_eligible"
    reference = (
        "https://leg.colorado.gov/laws/session-laws/HB24-1268/475/download#page=6",
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104EZ_2025.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.disability_assistance
        agi = tax_unit("adjusted_gross_income", period)
        joint = tax_unit("tax_unit_is_joint", period)
        return where(
            joint,
            p.amount.joint.calc(agi, right=True),
            p.amount.non_joint.calc(agi, right=True),
        )
