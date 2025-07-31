from policyengine_us.model_api import *


class mt_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Montana standard deduction when married couples are filing separately"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        # ▸ MT legacy parameter table (only relevant pre-2024)
        p = parameters(period).gov.states.mt.tax.income.deductions.standard

        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )

        if p.state_specific_deduction_applies:
            # ── Pre-2024 MT-specific calculation ────────────────────────────────
            agi = person("mt_agi", period)
            floor = p.floor[filing_status]
            cap = p.cap[filing_status]
            uncapped = p.rate * agi
            deduction_amount = max_(min_(uncapped, cap), floor)

        else:
            # ── 2024-onward: apply the *federal* standard-deduction variable ──

            deduction_amount = person.tax_unit("standard_deduction", period)

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return is_head_or_spouse * deduction_amount
