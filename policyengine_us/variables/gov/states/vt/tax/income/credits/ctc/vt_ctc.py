from policyengine_us.model_api import *


class vt_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont child tax credit"
    definition_period = YEAR
    unit = USD
    reference = "https://legislature.vermont.gov/statutes/section/32/151/05830f"
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        # 32 V.S.A. 5830f: a taxpayer entitled to a child tax credit under the
        # laws of the United States (or who would be but for the taxpayer
        # identification number requirements of IRC 24(e) and (h)(7)) gets the
        # credit for each qualifying child under IRC 152(c) at or under the
        # age limit. The identification waiver does not reach IRC 152(b)(1):
        # a return on which the filer (or, if joint, either spouse) can be
        # claimed as a dependent has no dependents and no federal credit.
        person = tax_unit.members
        age = person("age", period)
        p = parameters(period).gov.states.vt.tax.income.credits.ctc
        dependent = person("is_tax_unit_dependent", period)
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        eligible = (age <= p.age_limit) & dependent & ~filer_is_dependent
        count_eligible = tax_unit.sum(eligible)
        # Get adjusted gross income.
        agi = tax_unit("adjusted_gross_income", period)
        # 5830f(b): "the amount of the credit per child" is reduced, but not
        # below zero, by $20 for each $1,000 of AGI over $125,000.
        excess_agi = max_(agi - p.reduction.start, 0)
        increments = np.ceil(excess_agi / p.reduction.increment)
        reduction_per_child = p.reduction.amount * increments
        credit_per_child = max_(p.amount - reduction_per_child, 0)
        return count_eligible * credit_per_child
