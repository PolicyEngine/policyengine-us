from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciliation_qbid_with_floor() -> Reform:
    class qualified_business_income_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Qualified business income deduction for tax unit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
            "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
        )

        def formula(tax_unit, period, parameters):
            # compute sum of QBID amounts for each person in TaxUnit following
            # logic in 2018 IRS Publication 535, Worksheet 12-A, line 16
            person = tax_unit.members
            qbid_amt = person("qbid_amount", period)
            uncapped_qbid = tax_unit.sum(qbid_amt)
            # apply taxinc cap at the TaxUnit level following logic
            # in 2018 IRS Publication 535, Worksheet 12-A, lines 32-37
            taxinc_less_qbid = tax_unit("taxable_income_less_qbid", period)
            netcg_qdiv = tax_unit("adjusted_net_capital_gain", period)
            p = parameters(period).gov.irs.deductions.qbi.max
            taxinc_cap = p.rate * max_(0, taxinc_less_qbid - netcg_qdiv)
            pre_floor_qbid = min_(uncapped_qbid, taxinc_cap)
            p_ref = parameters(
                period
            ).gov.contrib.reconciliation.qbid.deduction_floor
            qualified_business_income = tax_unit(
                "qualified_business_income", period
            )
            floor = p_ref.amount.calc(qualified_business_income)
            return max_(pre_floor_qbid, floor)

    class reform(Reform):
        def apply(self):
            self.update_variable(qualified_business_income_deduction)

    return reform


def create_reconciliation_qbid_with_floor_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciliation_qbid_with_floor()

    p = parameters.gov.contrib.reconciliation.qbid.deduction_floor

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciliation_qbid_with_floor()
    else:
        return None


reconciliation_qbid_with_floor = create_reconciliation_qbid_with_floor_reform(
    None, None, bypass=True
)
