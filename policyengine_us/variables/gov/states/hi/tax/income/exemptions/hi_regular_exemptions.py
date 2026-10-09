from policyengine_us.model_api import *


class hi_regular_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii regular exemptions"
    unit = USD
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20",
        # HRS 235-54(a): the exemption of an individual whom another taxpayer
        # can claim "shall be zero", including the additional exemption for
        # age 65 or over.
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=45",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        # The federal count leaves out a filer who can be claimed as a
        # dependent and, on such a return, the dependents (HRS 235-54(a);
        # N-11 instructions: "You cannot claim any dependents").
        exemptions_count = tax_unit("exemptions_count", period)
        p = parameters(period).gov.states.hi.tax.income.exemptions
        # Aged heads and spouses who cannot be claimed get an extra base
        # exemption.
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        aged = person("age", period) >= p.aged_threshold
        aged_head_spouse_count = tax_unit.sum(aged & head_or_spouse & ~claimed)
        total_exemption_count_including_aged = exemptions_count + aged_head_spouse_count
        return total_exemption_count_including_aged * p.base
