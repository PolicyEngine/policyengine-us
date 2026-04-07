from policyengine_us.model_api import *
from policyengine_core.periods import instant
from policyengine_core.periods import period as period_


def create_ne_lb157_ctc() -> Reform:
    class ne_lb157_ctc_eligible_child(Variable):
        value_type = bool
        entity = Person
        label = "Nebraska LB 157 Child Tax Credit eligible child"
        definition_period = YEAR
        reference = (
            "https://nebraskalegislature.gov/bills/view_bill.php?DocumentID=58940"
        )
        defined_for = StateCode.NE

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.states.ne.ctc.lb157
            # Must be 6 or younger at end of tax year
            age = person("age", period)
            age_eligible = age <= p.age_limit
            # Must be claimed as dependent
            is_dependent = person("is_tax_unit_dependent", period)
            # Must have SSN or ITIN per Section 2(2)(c).
            # Note: The variable `has_itin` is named for historical reasons but actually
            # means "has ITIN or SSN" per its label. This matches the bill requirement
            # that the child be "issued either a social security number or an individual
            # taxpayer identification number."
            has_ssn_or_itin = person("has_itin", period)
            return age_eligible & is_dependent & has_ssn_or_itin

    class ne_lb157_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Nebraska LB 157 Child Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://nebraskalegislature.gov/bills/view_bill.php?DocumentID=58940"
        )
        defined_for = StateCode.NE

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ne.ctc.lb157
            # Count qualifying children
            qualifying_children = add(tax_unit, period, ["ne_lb157_ctc_eligible_child"])
            # Calculate base credit
            base_credit = p.amount * qualifying_children
            # Calculate phase-out
            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("adjusted_gross_income", period)
            threshold = p.phaseout.threshold[filing_status]
            increment = p.phaseout.increment[filing_status]
            rate = p.phaseout.rate
            # Number of increments (ceiling of excess / increment)
            excess = max_(agi - threshold, 0)
            # Use ceiling: any fraction of increment triggers phase-out
            increments = np.ceil(excess / increment)
            # Phase-out reduction per child (5% per increment)
            reduction_per_child = p.amount * rate * increments
            credit_per_child = max_(p.amount - reduction_per_child, 0)
            return credit_per_child * qualifying_children

    def modify_parameters(parameters):
        # Add ne_lb157_ctc to Nebraska refundable credits list
        refundable = parameters.gov.states.ne.tax.income.credits.refundable
        current_refundable = refundable(instant("2026-01-01"))
        if "ne_lb157_ctc" not in current_refundable:
            new_refundable = list(current_refundable) + ["ne_lb157_ctc"]
            refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2100-12-31"),
                value=new_refundable,
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(ne_lb157_ctc_eligible_child)
            self.update_variable(ne_lb157_ctc)
            self.modify_parameters(modify_parameters)

    return reform


def create_ne_lb157_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ne_lb157_ctc()

    p = parameters.gov.contrib.states.ne.ctc.lb157
    reform_active = False
    current_period = period_(period)
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ne_lb157_ctc()
    return None


ne_lb157_ctc = create_ne_lb157_ctc_reform(None, None, bypass=True)
