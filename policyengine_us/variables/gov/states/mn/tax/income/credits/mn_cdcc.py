from policyengine_us.model_api import *


class mn_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child and dependent care expense credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits
        person = tax_unit.members
        # determine eligibility for Minnesota CDCC
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status != filing_status.possible_values.SEPARATE
        # calculate number of qualifying dependents
        # ... children
        age = person("age", period)
        qualifies_by_age = age < p.cdcc.child_age
        # ... disability
        non_head = ~person("is_tax_unit_head", period)
        disabled = person("is_incapable_of_self_care", period)
        qualifies_by_disability = non_head & disabled
        dep_count = tax_unit.sum(qualifies_by_age | qualifies_by_disability)
        # calculate qualifying care expenses
        expense = tax_unit("tax_unit_childcare_expenses", period)
        # ... cap expense by number of qualifying dependents
        eligible_count = min_(dep_count, p.cdcc.maximum_dependents)
        expense = min_(expense, p.cdcc.maximum_expense * eligible_count)
        # ... cap expense by lower earnings of head and spouse if present
        expense = min_(expense, tax_unit("min_head_spouse_earned", period))
        # calculate pre-phaseout credit amount
        agi = tax_unit("adjusted_gross_income", period)
        pre_po_amount = expense * p.cdcc.expense_fraction.calc(agi)
        # calculate post-phaseout credit amount
        excess_agi = max_(0, agi - p.cdcc.phaseout_threshold)
        po_amount = excess_agi * p.cdcc.phaseout_rate
        amount = max_(0, pre_po_amount - po_amount)
        # credit amount only for eligibles
        return eligible * amount
