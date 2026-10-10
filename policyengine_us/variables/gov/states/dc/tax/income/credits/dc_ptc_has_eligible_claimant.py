from policyengine_us.model_api import *


class dc_ptc_has_eligible_claimant(Variable):
    value_type = bool
    entity = TaxUnit
    label = "DC property tax credit has an eligible claimant"
    documentation = (
        "Whether a filer in the tax unit can be the Schedule H claimant: no "
        "credit is allowed for a year in which the person claiming it was a "
        "dependent under an income tax law, unless that person is 65 or older. "
        "Only one claimant per tax filing unit may claim the credit, so a "
        "couple can claim it through either spouse."
    )
    definition_period = YEAR
    reference = (
        # D.C. Code 47-1806.06(b)(4) and (k).
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.06",
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.credits.ptc
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        old_enough = person("age", period) >= p.dependent_claimant_min_age
        return tax_unit.any(filer & (~claimed | old_enough))
