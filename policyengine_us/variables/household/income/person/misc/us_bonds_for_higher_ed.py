from policyengine_us.model_api import *


class us_bonds_for_higher_ed(Variable):
    value_type = float
    entity = Person
    label = "Income from U.S. bonds spent on higher education"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/135"
    documentation = (
        "Savings bond interest excluded under IRC 135 (Form 8815 line 14), "
        "taken as a deduction from gross income. Set it directly, or set the "
        "Form 8815 inputs (savings_bond_education_qualified_expenses and "
        "related) for PolicyEngine to compute it; it is assigned to the head."
    )

    def formula(person, period, parameters):
        proceeds = person.tax_unit("savings_bond_redemption_proceeds", period)
        if not np.any(proceeds > 0):
            # No Form 8815 inputs: skip the computation, which reads gross
            # income, so callers without them see no change.
            return np.zeros(person.count)
        head = person("is_tax_unit_head", period)
        return head * person.tax_unit("savings_bond_education_exclusion", period)
