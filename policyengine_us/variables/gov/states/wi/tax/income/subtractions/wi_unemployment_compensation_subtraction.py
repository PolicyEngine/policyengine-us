from policyengine_us.model_api import *


class wi_unemployment_compensation_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin unemployment compensation subtraction from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSB-Inst.pdf#page=1"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        us_tuc = add(tax_unit, period, ["taxable_unemployment_compensation"])
        us_agi = tax_unit("adjusted_gross_income", period)
        wi = parameters(period).gov.states.wi.tax.income
        p = wi.subtractions.unemployment_compensation.income_phase_out
        base_income = p.base[tax_unit("filing_status", period)]
        us_taxed_socsec = tax_unit("tax_unit_taxable_social_security", period)
        ucsub_income = base_income + us_taxed_socsec
        excess_inc = max_(0, us_agi - ucsub_income)
        tuc_limit = excess_inc * p.rate  # WI Unemploy Compen Worksheet, Line 8
        wi_tuc = min_(tuc_limit, us_tuc)
        return max_(0, us_tuc - wi_tuc)
