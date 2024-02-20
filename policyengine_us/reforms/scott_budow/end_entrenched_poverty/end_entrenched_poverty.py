from policyengine_us.model_api import *


def create_end_entrenched_poverty_credit() -> Reform:
    class end_entrenched_poverty_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Scott Budow's End Entrenched Poverty Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.scottbudow.com/issues?id=f5b39b46-f3ca-4fc8-a546-9229dbfbd487"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            income = tax_unit.household("household_net_income", period)
            federal_poverty_guidelines = tax_unit("tax_unit_fpg", period)
            children = tax_unit("tax_unit_children", period)
            p = parameters(
                period
            ).gov.contrib.scott_budow.end_entrenched_poverty
            fpg_ratio = income / federal_poverty_guidelines
            children_amount = (
                p.child.calc(fpg_ratio) * children
            ) * MONTHS_IN_YEAR
            adult_amount = p.adult.calc(fpg_ratio) * MONTHS_IN_YEAR
            return children_amount + adult_amount

    class ny_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            old_credits = add(
                tax_unit,
                period,
                parameters(period).gov.states.ny.tax.income.credits.refundable,
            )
            end_entrenched_poverty = tax_unit(
                "end_entrenched_poverty_credit", period
            )
            return old_credits + end_entrenched_poverty

    class reform(Reform):
        def apply(self):
            self.create_variable(end_entrenched_poverty_credit)
            self.update_variable(ny_refundable_credits)

    return reform


def create_end_entrenched_poverty_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_end_entrenched_poverty_credit()

    p = parameters(period).gov.contrib.scott_budow.end_entrenched_poverty

    if p.child.amounts[0] > 0:
        return create_end_entrenched_poverty_credit()

    else:
        return None


end_entrenched_poverty_credit = create_end_entrenched_poverty_credit_reform(
    None, None, bypass=True
)
