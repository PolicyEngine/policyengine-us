from policyengine_us.model_api import *


class mt_standard_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = (
        "Montana standard deduction when married couples are filing jointly"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        # Montana’s legacy parameter block (only applies through TY-2023)
        p = parameters(period).gov.states.mt.tax.income.deductions.standard

        filing_status = person.tax_unit("filing_status", period)

        if p.state_specific_deduction_applies:
            # ── Pre-2024 MT-specific calculation ───────────────────────────────
            agi = add(person.tax_unit, period, ["mt_agi"])
            floor = p.floor[filing_status]
            cap = p.cap[filing_status]
            uncapped = p.rate * agi
            deduction_amount = max_(min_(uncapped, cap), floor)

        else:
            # ── 2024-onward: just reuse the federal standard-deduction variable
            #     (That variable is defined on the TaxUnit entity.)
            deduction_amount = person.tax_unit("standard_deduction", period)
        # Only the tax-unit head records this joint amount
        is_head = person("is_tax_unit_head", period)
        return is_head * deduction_amount
