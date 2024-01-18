from policyengine_us.model_api import *


def create_ecpa_filer_credit() -> Reform:
    class ecpa_filer_credit(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "End Child Poverty Act Filer Credit"
        reference = "https://tlaib.house.gov/sites/tlaib.house.gov/files/EndChildPovertyAct.pdf"

        def formula_2022(tax_unit, period, parameters):
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

    class reform(Reform):
        def apply(self):
            self.update_variable(ecpa_filer_credit)

    return reform


def create_ecpa_filer_credit_reform(
     parameters, period, tax_unit, bypass: bool = False,
):
    if bypass:
        return create_ecpa_filer_credit()

    filing_status = tax_unit("filing_status", period)

    p = parameters(
        period
    ).gov.contrib.congress.tlaib.end_child_poverty_act.filer_credit


    if p.amount[filing_status] > 0:
        return create_ecpa_filer_credit()
    else:
        return None


ecpa_filer_credit = create_ecpa_filer_credit_reform( None, None, None, bypass=True)
