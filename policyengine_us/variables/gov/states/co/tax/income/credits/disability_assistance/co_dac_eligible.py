from policyengine_us.model_api import *


class co_dac_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado Disability Assistance Credit"
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = (
        "https://leg.colorado.gov/laws/session-laws/HB24-1268/475/download#page=6",
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104EZ_2025.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.disability_assistance
        if not p.in_effect:
            return False

        person = tax_unit.members
        qualified = (
            person("co_dac_disability_qualified", period)
            & person("co_dac_resident_qualified", period)
            & person("is_tax_unit_head_or_spouse", period)
        )
        agi = tax_unit("adjusted_gross_income", period)
        joint = tax_unit("tax_unit_is_joint", period)
        amount = where(
            joint,
            p.amount.joint.calc(agi, right=True),
            p.amount.non_joint.calc(agi, right=True),
        )
        return (
            (tax_unit.sum(qualified) > 0)
            & (amount > 0)
            & ~tax_unit("co_ptc_elected", period)
        )
