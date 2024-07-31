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
    defined_for = "wi_homestead_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        uncapped_ptax = tax_unit("wi_homestead_property_tax", period)
        capped_ptax = min_(p.homestead.property_tax.max, uncapped_ptax)
        hincome = tax_unit("wi_homestead_income", period)
        phase_out_start = p.homestead.phase_out.start
        phase_out_rate = p.homestead.phase_out.rate
        phase_out = max_(0, hincome - phase_out_start) * phase_out_rate
        return max_(0, capped_ptax - phase_out) * p.homestead.rate
