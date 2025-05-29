from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_qbid() -> Reform:
    class qbid_amount(Variable):
        value_type = float
        entity = Person
        label = "Per‑cap qualified business income deduction amount for each person"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
            "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
        )

        def formula(person, period, parameters):
            p = parameters(period).gov.irs.deductions

            # 1. Compute the new maximum QBID
            qbi = person("qualified_business_income", period)
            qbid_max = p.qbi.max.rate * qbi

            # 2. Compute the wage/property cap (unchanged)
            w2_wages = person("w2_wages_from_qualified_business", period)
            b_property = person("unadjusted_basis_qualified_property", period)
            wage_cap = w2_wages * p.qbi.max.w2_wages.rate
            alt_cap = (
                w2_wages * p.qbi.max.w2_wages.alt_rate
                + b_property * p.qbi.max.business_property.rate
            )
            full_cap = max_(wage_cap, alt_cap)

            # 3. Phase‑out logic: 75% of each dollar above the threshold
            taxinc_less_qbid = person.tax_unit(
                "taxable_income_less_qbid", period
            )
            filing_status = person.tax_unit("filing_status", period)
            threshold = p.qbi.phase_out.start[filing_status]
            p_ref = parameters(period).gov.contrib.reconciliation.qbid
            phase_out_rate = p_ref.phase_out_rate
            excess_income = max_(0, taxinc_less_qbid - threshold)
            reduction_amount = phase_out_rate * excess_income
            # 4. Apply phase‑out to the 22% deduction
            phased_deduction = max_(0, qbid_max - reduction_amount)
            # 5. Final QBID is the lesser of the phased deduction or the wage/property cap
            return min_(phased_deduction, full_cap)

    class reform(Reform):
        def apply(self):
            self.update_variable(qbid_amount)

    return reform


def create_reconciled_qbid_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_reconciled_qbid()

    p = parameters.gov.contrib.reconciliation.qbid

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_qbid()
    else:
        return None


reconciled_qbid = create_reconciled_qbid_reform(None, None, bypass=True)
