from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_or_dependent_exemption_credit_reform() -> Reform:
    class or_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = (
            "Oregon eligible dependents count for dependent exemption credit"
        )
        definition_period = YEAR
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            p = (
                parameters(period)
                .gov.contrib.states["or"]
                .dependent_exemption_credit
            )

            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)

            # Apply age limit if in effect
            age_threshold = p.age_limit.threshold
            age_eligible = age < age_threshold
            eligible_dependents = where(
                p.age_limit.in_effect,
                is_dependent & age_eligible,
                is_dependent,
            )

            return tax_unit.sum(eligible_dependents)

    class or_older_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Oregon older dependents count (excluded from dependent exemption credit)"
        definition_period = YEAR
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependents = tax_unit(
                "or_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependents)

    class or_dependent_exemption_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Oregon dependent exemption credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            p = (
                parameters(period)
                .gov.contrib.states["or"]
                .dependent_exemption_credit
            )

            eligible_count = tax_unit("or_eligible_dependents_count", period)
            maximum_credit = eligible_count * p.amount

            # Apply income limit (cliff cutoff) unless universal mode is enabled
            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("adjusted_gross_income", period)
            income_limit = p.income_limit[filing_status]
            qualifies = agi <= income_limit

            # Universal mode bypasses income limit
            effective_qualifies = where(p.phaseout.in_effect, True, qualifies)

            return where(effective_qualifies, maximum_credit, 0)

    class or_regular_exemptions(Variable):
        value_type = int
        entity = TaxUnit
        label = "Oregon regular exemptions"
        definition_period = YEAR
        reference = (
            "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17",
            "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",
        )
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            filing_status = tax_unit("filing_status", period)
            federal_agi = tax_unit("adjusted_gross_income", period)
            p = (
                parameters(period)
                .gov.states["or"]
                .tax.income.credits.exemption
            )

            qualifies = federal_agi <= p.income_limit.regular[filing_status]

            # Count head and spouse only (1 for single/hoh, 2 for joint)
            head_spouse_count = where(
                filing_status == filing_status.possible_values.JOINT, 2, 1
            )

            # Add older dependents (those excluded from dependent credit by age limit)
            older_dependents = tax_unit("or_older_dependents_count", period)

            return qualifies * (head_spouse_count + older_dependents)

    class or_exemption_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Oregon exemption credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17",
            "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",
        )
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            EXEMPTION_TYPES = [
                "regular",
                "severely_disabled",
                "disabled_child_dependent",
            ]
            exemptions = add(
                tax_unit,
                period,
                ["or_" + i + "_exemptions" for i in EXEMPTION_TYPES],
            )
            amount = (
                parameters(period)
                .gov.states["or"]
                .tax.income.credits.exemption.amount
            )
            base_credit = exemptions * amount

            # Add the dependent exemption credit (uses contrib amount)
            dependent_credit = tax_unit(
                "or_dependent_exemption_credit", period
            )

            return base_credit + dependent_credit

    class reform(Reform):
        def apply(self):
            self.update_variable(or_eligible_dependents_count)
            self.update_variable(or_older_dependents_count)
            self.update_variable(or_dependent_exemption_credit)
            self.update_variable(or_regular_exemptions)
            self.update_variable(or_exemption_credit)

    return reform


def create_or_dependent_exemption_credit_reform_fn(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_or_dependent_exemption_credit_reform()

    p = getattr(parameters.gov.contrib.states, "or").dependent_exemption_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_or_dependent_exemption_credit_reform()
    else:
        return None


or_dependent_exemption_credit_reform = (
    create_or_dependent_exemption_credit_reform_fn(None, None, bypass=True)
)
