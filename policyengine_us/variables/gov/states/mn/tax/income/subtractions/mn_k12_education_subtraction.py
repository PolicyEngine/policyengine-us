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
        return tax_unit.sum(where(qualifying, min_(expenses, cap), 0))
