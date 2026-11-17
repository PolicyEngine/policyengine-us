from policyengine_us.model_api import *


def il_aabd_child_care_exemption(person, period, parameters, childcare_expenses):
    """Illinois AABD child care expense exemption for one month.

    89 Ill. Adm. Code 113.125(b) caps the exemption by hours worked and the
    number of children. ``childcare_expenses`` is the SPM unit's monthly child
    care cost, projected to each person.
    """
    p = parameters(period).gov.states.il.dhs.aabd.income.exemption
    have_childcare_expenses = childcare_expenses > 0
    monthly_hours_worked = person("monthly_hours_worked", period)
    child_count = person.tax_unit("tax_unit_dependents", period)
    childcare_exemption = (
        p.child_care.calc(monthly_hours_worked) * child_count * have_childcare_expenses
    )
    child_care_expense_exemption = min_(childcare_expenses, childcare_exemption)
    # Attributing the dependent care expense exemption equally to each spouse if filing jointly
    is_married = person.family("is_married", period)
    expense_amount = where(
        is_married,
        child_care_expense_exemption / 2,
        child_care_expense_exemption,
    )
    is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    return is_head_or_spouse * expense_amount
