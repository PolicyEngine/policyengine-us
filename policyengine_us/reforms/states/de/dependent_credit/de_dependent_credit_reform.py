from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_de_dependent_credit_reform() -> Reform:
    class de_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Delaware eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.DE

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.de.dependent_credit

            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)

            # Apply age limit if in effect
            if p.age_limit.in_effect:
                age_threshold = p.age_limit.threshold
                eligible_dependents = is_dependent & (age < age_threshold)
            else:
                eligible_dependents = is_dependent

            return tax_unit.sum(eligible_dependents)

    class de_dependent_credit_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Delaware dependent credit maximum before phaseout"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.DE

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.de.dependent_credit

            dependents_count = tax_unit("de_eligible_dependents_count", period)
            return dependents_count * p.amount

    class de_dependent_credit_phaseout(Variable):
        value_type = float
        entity = TaxUnit
        label = "Delaware dependent credit phaseout amount"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.DE

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.de.dependent_credit

            filing_status = tax_unit("filing_status", period)
            files_separately = tax_unit("de_files_separately", period)
            agi_indiv = add(tax_unit, period, ["de_agi_indiv"])
            agi_joint = add(tax_unit, period, ["de_agi_joint"])
            agi = where(files_separately, agi_indiv, agi_joint)

            threshold = p.phaseout.threshold[filing_status]
            excess_income = max_(agi - threshold, 0)
            return excess_income * p.phaseout.rate

    class de_dependent_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Delaware dependent credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.DE

        def formula(tax_unit, period, parameters):

            maximum = tax_unit("de_dependent_credit_maximum", period)
            phaseout = tax_unit("de_dependent_credit_phaseout", period)

            return max_(maximum - phaseout, 0)

    class de_older_dependents_count(Variable):
        value_type = float
        entity = TaxUnit
        label = "Delaware older dependents count"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.DE

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependent_credit = tax_unit(
                "de_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependent_credit)

    class de_personal_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Delaware personal credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.DE

        def formula(tax_unit, period, parameters):
            p_base = parameters(
                period
            ).gov.states.de.tax.income.credits.personal_credits

            # Calculate personal credit base amount (head + spouse + older dependents)
            filing_status = tax_unit("filing_status", period)
            older_dependents = tax_unit("de_older_dependents_count", period)
            personal_count = (
                where(
                    filing_status == filing_status.possible_values.JOINT,
                    2,
                    1,
                )
                + older_dependents
            )
            personal_credit_amount = personal_count * p_base.personal

            # Add dependent credit (has its own phase-out logic)
            dependent_credit_amount = tax_unit("de_dependent_credit", period)

            return personal_credit_amount + dependent_credit_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(de_eligible_dependents_count)
            self.update_variable(de_dependent_credit_maximum)
            self.update_variable(de_dependent_credit_phaseout)
            self.update_variable(de_dependent_credit)
            self.update_variable(de_older_dependents_count)
            self.update_variable(de_personal_credit)

    return reform


def create_de_dependent_credit_reform_fn(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_de_dependent_credit_reform()

    p = parameters.gov.contrib.states.de.dependent_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_de_dependent_credit_reform()
    else:
        return None


de_dependent_credit_reform = create_de_dependent_credit_reform_fn(
    None, None, bypass=True
)
