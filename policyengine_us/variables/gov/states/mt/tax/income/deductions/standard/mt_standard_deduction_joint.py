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
        # Get the current year
        year = period.start.year
        p = parameters(period).gov.states.mt.tax.income.deductions.standard
        # Get filing status
        filing_status = person.tax_unit("filing_status", period)

        if p.applies:
            # Pre-2024: MT specific standard deduction calculation
            p = parameters(period).gov.states.mt.tax.income.deductions.standard
            agi = add(person.tax_unit, period, ["mt_agi"])
            # standard deduction is a percentage of AGI that
            # is bounded by a min/max by filing status.
            floor = p.floor[filing_status]
            cap = p.cap[filing_status]
            uncapped_amount = p.rate * agi
            capped_amount = min_(uncapped_amount, cap
            deduction_amount = max_(capped_amount, floor)
        else:
            # 2024 and after: Use federal standard deduction
            std = parameters(period).gov.irs.deductions.standard
            deduction_amount = std.amount[filing_status]

        is_head = person("is_tax_unit_head", period)
        return is_head * deduction_amount
