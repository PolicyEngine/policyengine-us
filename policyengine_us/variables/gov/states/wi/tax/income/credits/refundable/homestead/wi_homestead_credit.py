from policyengine_us.model_api import *


class wi_homestead_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin homestead credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=3"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=27"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=3"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=28"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits.refundable
        uncapped_ptax = tax_unit("wi_homestead_property_tax", period)
        capped_ptax = min_(p.homestead.property_tax.max, uncapped_ptax)
        hinc = tax_unit("wi_homestead_income", period)
        phase_out = where(
            hinc <= p.homestead.phase_out.start,
            0,
            (hinc - p.homestead.phase_out.start) * p.homestead.phase_out.rate,
        )
        hcredit = max_(0, capped_ptax - phase_out) * p.homestead.rate
        eligible = tax_unit("wi_homestead_eligible", period)
        return eligible * hcredit
