from policyengine_us.model_api import *


class hi_disabled_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii disabled exemptions"
    unit = USD
    reference = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.hi.tax.income.exemptions
        # The tax unit can claim exemptions for each dependent
        dependents = tax_unit("tax_unit_dependents", period)
        # If the head or the spouse is disabled, they take the disabled rather than dependent exemption.
        disabled = person("is_disabled", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disabled_head_or_spouse = disabled & head_or_spouse
        any_disabled_head_or_spouse = tax_unit.any(disabled & head_or_spouse)
        dependent_amount = p.base * dependents
        conditional_dependent_amount = where(
            any_disabled_head_or_spouse, 0, dependent_amount
        )
        aged = person("age", period) >= p.aged_threshold
        # Filer can claim greater of the disabled or base exemption. HRS
        # 235-54(c) and HAR 18-235-54(c) grant the $7,000 exemption "instead
        # of the exemptions provided by subsection (a)" without a dependency
        # bar, so a disabled filer keeps it even if another taxpayer can
        # claim them.
        disabled_exemption = disabled_head_or_spouse * p.disabled
        # Aged individuals get an extra base exemption. Under HRS 235-54(a)
        # the regular and aged exemptions of a filer whom another taxpayer
        # can claim are zero.
        claimed = person("claimed_as_dependent_on_another_return", period)
        head_or_spouse_amount = p.base * (1 + aged) * head_or_spouse * ~claimed
        conditional_head_or_spouse_amount = max_(
            disabled_exemption, head_or_spouse_amount
        )
        total_conditional_head_or_spouse_amount = tax_unit.sum(
            conditional_head_or_spouse_amount
        )
        total_amount = (
            conditional_dependent_amount + total_conditional_head_or_spouse_amount
        )
        return where(any_disabled_head_or_spouse, total_amount, 0)
