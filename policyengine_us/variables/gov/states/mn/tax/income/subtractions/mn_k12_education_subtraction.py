from policyengine_us.model_api import *


class mn_k12_education_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota K-12 Education Expense Subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.4",
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1m-25.pdf#page=5",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.subtractions.k12_education
        person = tax_unit.members
        # Minn. Stat. 290.0132 subd. 4 caps the subtraction for each
        # qualifying child separately: the lower amount for a child in
        # kindergarten to grade 6 and the higher amount for a child in grades
        # 7 to 12. Each child's expenses are capped on their own, so one
        # child's unused cap does not carry to another.
        # A proxy, as in mn_k12_qualifying_children: 290.0674 subd. 1a(d) gives
        # "qualifying child" its IRC 32(c)(3) meaning, which doesn't turn on
        # dependency for an unmarried child.
        qualifying = person("is_in_k12_school", period) & person(
            "is_tax_unit_dependent", period
        )
        expenses = max_(
            person("mn_k12_education_subtraction_qualifying_expenses_person", period),
            0,
        )
        cap = where(
            person("mn_k12_education_subtraction_higher_cap_eligible", period),
            p.cap.higher,
            p.cap.lower,
        )
        child_expenses = where(qualifying, expenses, 0)
        child_caps = where(qualifying, cap, 0)
        per_child = tax_unit.sum(min_(child_expenses, child_caps))
        # A household may hold only the tax unit's total, which the K-12
        # credit also reads. That total can't be split by child, so it meets
        # the sum of the children's caps.
        unit_total = max_(tax_unit("k12_tuition_and_fees", period), 0)
        pooled = min_(unit_total, tax_unit.sum(child_caps))
        has_child_records = tax_unit.sum(child_expenses) > 0
        return where(has_child_records, per_child, pooled)
