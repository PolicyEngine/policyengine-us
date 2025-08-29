from policyengine_us.model_api import *


class ecpa_filer_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "End Child Poverty Act filer credit"
    unit = USD
    documentation = (
        "Filer credit under the End Child Poverty Act for eligible tax filers"
    )
    reference = "placeholder - bill not yet introduced"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act

        if not p.in_effect:
            return tax_unit("adjusted_gross_income", period) * 0

        person = tax_unit.members
        age = person("age", period)
        min_age = p.filer_credit.eligibility.min_age

        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        is_filer = is_head | is_spouse

        is_eligible_age = (age >= min_age) & (age < 65)
        is_eligible_filer = is_filer & is_eligible_age

        has_eligible_filer = tax_unit.any(is_eligible_filer)

        filing_status = tax_unit("filing_status", period)
        amount = p.filer_credit.amount[filing_status]

        agi = tax_unit("adjusted_gross_income", period)
        phase_out_start = p.filer_credit.phase_out.start[filing_status]
        phase_out_rate = p.filer_credit.phase_out.rate

        excess_agi = max_(agi - phase_out_start, 0)
        phase_out = excess_agi * phase_out_rate

        credit = max_(amount - phase_out, 0)

        return has_eligible_filer * credit
