from policyengine_us.model_api import *


def create_co_family_affordability_credit() -> Reform:
    class co_family_affordability_credit(Variable):
        value_type = float
        entity = Person
        label = "Colorado Family Affordability Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://leg.colorado.gov/bills/hb24-1311"
        defined_for = StateCode.CO

        def formula(person, period, parameters):
            age = person("age", period)
            dependent = person("is_child_dependent", period)
            p = parameters(
                period
            ).gov.contrib.co_general_assembly.family_affordability_credit
            base_amount = p.amount.calc(age) * dependent
            agi = person.tax_unit("adjusted_gross_income", period)
            filing_status = person.tax_unit("filing_status", period)
            # The phase-out amounts, start points, and increments are differently defined
            # for younger and older dependents.
            young_child = age < p.amount.thresholds[1]
            phase_out_start = where(
                young_child,
                p.reduction.younger.start[filing_status],
                p.reduction.older.start[filing_status],
            )
            phase_out_amount = where(
                young_child,
                p.reduction.younger.amount,
                p.reduction.older.amount,
            )
            phase_out_increment = where(
                young_child,
                p.reduction.younger.increment,
                p.reduction.older.increment,
            )
            excess = max_(agi - phase_out_start, 0)
            increments = np.ceil(excess / phase_out_increment)
            amount = increments * phase_out_amount
            return max_(base_amount - amount, 0)

    class co_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Colorado refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.CO

        def formula(tax_unit, period, parameters):
            old_credits = parameters(
                period
            ).gov.states.co.tax.income.credits.refundable
            all_credits = old_credits + ["co_family_affordability_credit"]
            return add(tax_unit, period, all_credits)

    class reform(Reform):
        def apply(self):
            self.add_variable(co_family_affordability_credit)
            self.update_variable(co_refundable_credits)

    return reform


def create_co_family_affordability_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_co_family_affordability_credit()

    p = parameters(
        period
    ).gov.contrib.co_general_assembly.family_affordability_credit

    if (p.amount.amounts[0] > 0) | (p.amount.amounts[1] > 0):
        return create_co_family_affordability_credit()

    else:
        return None


co_family_affordability_credit = create_co_family_affordability_credit_reform(
    None, None, bypass=True
)
