from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ri_ctc() -> Reform:
    class ri_ctc_eligible_children(Variable):
        value_type = int
        entity = TaxUnit
        label = "Rhode Island CTC eligible children count"
        unit = "#"
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

    class ri_ctc_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island CTC maximum amount before phaseout"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            eligible_children = tax_unit("ri_ctc_eligible_children", period)
            return eligible_children * p.amount

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
            phaseout = 0

            # Check AGI-based phaseout
            if p.phaseout.agi_based.in_effect:
                income = tax_unit("ri_agi", period)
                threshold = p.phaseout.agi_based.threshold[filing_status]
                excess_income = max_(income - threshold, 0)
                phaseout = excess_income * p.phaseout.agi_based.rate

            # Check earnings-based phaseout
            elif p.phaseout.earnings_based.in_effect:
                income = tax_unit("tax_unit_earned_income", period)
                threshold = p.phaseout.earnings_based.threshold[filing_status]
                excess_income = max_(income - threshold, 0)
                phaseout = excess_income * p.phaseout.earnings_based.rate

            return phaseout

    class ri_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island Child Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI
        reference = (
            "https://github.com/PolicyEngine/policyengine-us/issues/6642"
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            # Calculate maximum credit
            maximum = tax_unit("ri_ctc_maximum", period)

            # Apply phaseout
            phaseout = tax_unit("ri_ctc_phaseout", period)
            credit_after_phaseout = max_(maximum - phaseout, 0)

            return credit_after_phaseout

    class ri_ctc_refundable(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island CTC refundable portion"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            total_credit = tax_unit("ri_ctc", period)

            # Check refundability options
            if p.refundability.fully_refundable.in_effect:
                return total_credit
            elif p.refundability.partially_refundable.in_effect:
                return min_(
                    total_credit, p.refundability.partially_refundable.cap
                )
            else:  # Nonrefundable
                return 0

    class ri_ctc_nonrefundable(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island CTC non-refundable portion"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.ctc

            total_credit = tax_unit("ri_ctc", period)
            refundable_portion = tax_unit("ri_ctc_refundable", period)
            return total_credit - refundable_portion

    def modify_parameters(parameters):
        # Add ri_ctc to refundable credits list if any refundable option is active
        refundable = parameters.gov.states.ri.tax.income.credits.refundable
        current_credits = refundable(instant("2025-01-01"))
        if "ri_ctc" not in current_credits:
            new_credits = list(current_credits) + ["ri_ctc"]
            refundable.update(
                start=instant("2025-01-01"),
                stop=instant("2100-12-31"),
                value=new_credits,
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(ri_ctc_eligible_children)
            self.update_variable(ri_ctc_maximum)
            self.update_variable(ri_ctc_phaseout)
            self.update_variable(ri_ctc)
            self.update_variable(ri_ctc_refundable)
            self.update_variable(ri_ctc_nonrefundable)
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
