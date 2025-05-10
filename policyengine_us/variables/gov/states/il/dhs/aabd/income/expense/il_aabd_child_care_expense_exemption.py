from policyengine_us.model_api import *


class il_aabd_child_care_expense_exemption(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) childcare expense exemption"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.125",  # b
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.income.exemption
        childcare_expenses = person.spm_unit("childcare_expenses", period)
        have_childcare_expenses = childcare_expenses > 0
        weekly_hours_worked = person("weekly_hours_worked_before_lsr", period)* MONTHS_IN_YEAR
        child_count = person.tax_unit("tax_unit_dependents",period)
        childcare_exemption = (
            p.child_care.calc(weekly_hours_worked)
            * child_count
            * have_childcare_expenses
        )
        child_care_expense_exemption = min_(
            childcare_expenses, childcare_exemption
        )
        filing_status = person.tax_unit("filing_status", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        joint = filing_status == filing_status.possible_values.JOINT
        # Attributing the dependent care deduction equally to each spouse if filing jointly
        expense_amount = where(
            joint,
            child_care_expense_exemption / 2,
            child_care_expense_exemption,
        )
        return is_head_or_spouse * expense_amount
