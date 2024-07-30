from policyengine_us.model_api import *


def create_end_child_poverty_act() -> Reform:

    class ecpa_adult_dependent_credit(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "End Child Poverty Act Adult Dependent Credit"

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.end_child_poverty_act.adult_dependent_credit
            # Adult dependent credit.
            dependent = person("is_tax_unit_dependent", period)
            adult = person("age", period) >= p.min_age
            return p.amount * tax_unit.sum(adult & dependent)

    class ecpa_filer_credit(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "End Child Poverty Act Filer Credit"
        reference = "https://tlaib.house.gov/sites/tlaib.house.gov/files/EndChildPovertyAct.pdf"

        def formula(tax_unit, period, parameters):
            # Filer credit.
            # Define eligibility based on age.
            age_head = tax_unit("age_head", period)
            age_spouse = tax_unit("age_spouse", period)
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.end_child_poverty_act.filer_credit

            head_qualifies = (age_head >= p.eligibility.min_age) & (
                age_head <= p.eligibility.max_age
            )
            spouse_qualifies = (age_spouse >= p.eligibility.min_age) & (
                age_spouse <= p.eligibility.max_age
            )
            filer_credit_eligible = head_qualifies | spouse_qualifies
            # Get maximum amount.
            filing_status = tax_unit("filing_status", period)
            max_filer_credit = p.amount[filing_status]
            # Phase out.
            agi = tax_unit("adjusted_gross_income", period)
            phase_out_start = p.phase_out.start[filing_status]
            excess = max_(agi - phase_out_start, 0)
            reduction = excess * p.phase_out.rate
            # Compute final amount.
            return filer_credit_eligible * max_(
                max_filer_credit - reduction, 0
            )

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits
            previous_credits = add(tax_unit, period, p.refundable)
            filer_credit = tax_unit("ecpa_filer_credit", period)
            adult_dependent_credit = tax_unit(
                "ecpa_adult_dependent_credit", period
            )
            return filer_credit + adult_dependent_credit + previous_credits

    class reform(Reform):
        def apply(self):
            self.update_variable(ecpa_adult_dependent_credit)
            self.update_variable(ecpa_filer_credit)
            self.update_variable(income_tax_refundable_credits)
            self.neutralize_variable("eitc")
            self.neutralize_variable("ctc")

    return reform


def create_end_child_poverty_act_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_end_child_poverty_act()

    p = parameters(period).gov.contrib.congress.tlaib.end_child_poverty_act

    if p.in_effect:
        return create_end_child_poverty_act()
    else:
        return None


end_child_poverty_act = create_end_child_poverty_act_reform(
    None, None, bypass=True
)
