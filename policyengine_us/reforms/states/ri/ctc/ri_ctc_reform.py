from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ri_ctc() -> Reform:
    class ri_ctc_eligible_children(Variable):
        value_type = int
        entity = TaxUnit
        label = "Rhode Island CTC eligible children count"
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)

            # Check age eligibility
            meets_age = age < p.age_limit

            eligible = is_dependent & meets_age
            return tax_unit.sum(eligible)

    class ri_ctc_young_child_boost(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island CTC young child boost"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)

            # Check both general CTC eligibility and young child age limit
            meets_age = age < p.age_limit
            meets_young_child_age = age < p.young_child_boost.age_limit

            eligible_young_children = tax_unit.sum(
                is_dependent & meets_age & meets_young_child_age
            )
            return eligible_young_children * p.young_child_boost.amount

    class ri_ctc_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island CTC maximum amount before phaseout"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            # Base credit for all eligible children
            eligible_children = tax_unit("ri_ctc_eligible_children", period)
            base_credit = eligible_children * p.amount

            # Young child boost
            young_child_boost = tax_unit("ri_ctc_young_child_boost", period)

            return base_credit + young_child_boost

    class ri_ctc_phaseout(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island CTC phaseout amount"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("ri_agi", period)

            threshold = p.phaseout.threshold[filing_status]
            excess_income = max_(agi - threshold, 0)
            return excess_income * p.phaseout.rate

    class ri_total_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island Child Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            # Calculate maximum credit
            maximum = tax_unit("ri_ctc_maximum", period)

            # Apply phaseout
            phaseout = tax_unit("ri_ctc_phaseout", period)

            return max_(maximum - phaseout, 0)

    class ri_refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island CTC refundable portion"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            total_credit = tax_unit("ri_total_ctc", period)

            # The refundable portion is the minimum of the cap and total credit
            # This ensures the refundable amount never exceeds the total credit
            # - If cap = 0: credit is nonrefundable
            # - If 0 < cap < total_credit: credit is partially refundable
            # - If cap >= total_credit: credit is fully refundable
            return min_(total_credit, p.refundability.cap)

    class ri_non_refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island CTC non-refundable portion"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            total_credit = tax_unit("ri_total_ctc", period)
            refundable_portion = tax_unit("ri_refundable_ctc", period)
            return max_(total_credit - refundable_portion, 0)

    def modify_parameters(parameters):
        # Add ri_refundable_ctc to refundable credits list
        refundable = parameters.gov.states.ri.tax.income.credits.refundable
        current_refundable = refundable(instant("2025-01-01"))
        if "ri_refundable_ctc" not in current_refundable:
            new_refundable = list(current_refundable) + ["ri_refundable_ctc"]
            refundable.update(
                start=instant("2025-01-01"),
                stop=instant("2100-12-31"),
                value=new_refundable,
            )

        # Add ri_non_refundable_ctc to non-refundable credits list
        non_refundable = (
            parameters.gov.states.ri.tax.income.credits.non_refundable
        )
        current_non_refundable = non_refundable(instant("2025-01-01"))
        if "ri_non_refundable_ctc" not in current_non_refundable:
            new_non_refundable = list(current_non_refundable) + [
                "ri_non_refundable_ctc"
            ]
            non_refundable.update(
                start=instant("2025-01-01"),
                stop=instant("2100-12-31"),
                value=new_non_refundable,
            )

        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(ri_ctc_eligible_children)
            self.update_variable(ri_ctc_young_child_boost)
            self.update_variable(ri_ctc_maximum)
            self.update_variable(ri_ctc_phaseout)
            self.update_variable(ri_total_ctc)
            self.update_variable(ri_refundable_ctc)
            self.update_variable(ri_non_refundable_ctc)
            self.modify_parameters(modify_parameters)

    return reform


def create_ri_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ri_ctc()

    p = parameters.gov.contrib.states.ri.ctc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ri_ctc()
    else:
        return None


ri_ctc = create_ri_ctc_reform(None, None, bypass=True)
