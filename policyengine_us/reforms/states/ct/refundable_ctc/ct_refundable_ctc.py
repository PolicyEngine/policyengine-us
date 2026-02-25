from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ct_refundable_ctc() -> Reform:
    class ct_refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Connecticut refundable child tax credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.cga.ct.gov/2026/TOB/H/PDF/2026HB-05134-R00-HB.PDF#page=2"
        defined_for = StateCode.CT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ct.refundable_ctc

            # Count qualifying children (dependents under age limit)
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            age = person("age", period)
            is_child = is_dependent & (age < p.age_limit)
            qualifying_children = tax_unit.sum(is_child)
            capped_children = min_(qualifying_children, p.max_children)

            # Calculate credit amount
            credit_amount = capped_children * p.amount

            # Check income eligibility.
            # HB 5134: "less than" $100K for single filers (strict <),
            # "$200K or less" for joint filers (<=).
            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            income_threshold = p.income_threshold[filing_status]
            joint = filing_status.possible_values.JOINT
            surviving_spouse = filing_status.possible_values.SURVIVING_SPOUSE
            uses_joint_threshold = (filing_status == joint) | (
                filing_status == surviving_spouse
            )
            income_eligible = where(
                uses_joint_threshold,
                agi <= income_threshold,
                agi < income_threshold,
            )

            return income_eligible * credit_amount

    def modify_parameters(parameters):
        parameters.gov.states.ct.tax.income.credits.refundable.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=["ct_eitc", "ct_refundable_ctc"],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(ct_refundable_ctc)
            self.modify_parameters(modify_parameters)

    return reform


def create_ct_refundable_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ct_refundable_ctc()

    p = parameters.gov.contrib.states.ct.refundable_ctc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ct_refundable_ctc()
    else:
        return None


ct_refundable_ctc = create_ct_refundable_ctc_reform(None, None, bypass=True)
