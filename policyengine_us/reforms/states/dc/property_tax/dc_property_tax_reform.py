from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_dc_property_tax_credit() -> Reform:
    class dc_ptc(Variable):
        value_type = float
        entity = TaxUnit
        label = "DC property tax credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=49"
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=47"
        )
        defined_for = "takes_up_dc_ptc"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.dc.property_tax
            filing_status = tax_unit("filing_status", period)
            amount = p.amount[filing_status]
            # Income based eligibility criteria does not apply when the credit
            # is phased out.
            eligible = tax_unit("dc_ptc_eligible", period)
            if p.phase_out.applies:
                income_limit = tax_unit("dc_ptc_income_limit", period)
                income = tax_unit("adjusted_gross_income", period)
                income_excess = max_(0, income - income_limit)
                return max_(0, amount - p.phase_out.rate * income_excess)
            return amount * eligible

    class dc_ptc_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "DC property tax credit eligible"
        definition_period = YEAR
        reference = (
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=49"
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=47"
        )
        defined_for = StateCode.DC

        def formula(tax_unit, period, parameters):
            us_agi = tax_unit("adjusted_gross_income", period)
            income_limt = tax_unit("dc_ptc_income_limit", period)
            return us_agi <= income_limt

    class dc_ptc_income_limit(Variable):
        value_type = float
        entity = TaxUnit
        unit = USD
        label = "DC property tax credit income limit"
        definition_period = YEAR
        reference = (
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=49"
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=47"
        )
        defined_for = StateCode.DC

        def formula(tax_unit, period, parameters):
            elderly_present = tax_unit(
                "dc_ptc_elderly_head_or_spouse_present", period
            )
            filing_status = tax_unit("filing_status", period)
            p = parameters(
                period
            ).gov.contrib.states.dc.property_tax.income_limit
            return where(
                elderly_present,
                p.elderly[filing_status],
                p.non_elderly[filing_status],
            )

    class dc_ptc_elderly_head_or_spouse_present(Variable):
        value_type = bool
        entity = TaxUnit
        label = "DC property tax credit elderly head or spouse present"
        definition_period = YEAR
        reference = (
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=49"
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=47"
        )
        defined_for = StateCode.DC

        def formula(tax_unit, period, parameters):
            p_dc = parameters(period).gov.states.dc.tax.income.credits
            elderly_age = p_dc.ptc.min_elderly_age
            head_age = tax_unit("age_head", period)
            spouse_age = tax_unit("age_spouse", period)
            return (head_age >= elderly_age) | (spouse_age >= elderly_age)

    class reform(Reform):
        def apply(self):
            self.update_variable(dc_ptc)
            self.update_variable(dc_ptc_eligible)
            self.update_variable(dc_ptc_income_limit)
            self.update_variable(dc_ptc_elderly_head_or_spouse_present)

    return reform


def create_dc_property_tax_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_dc_property_tax_credit()

    p = parameters.gov.contrib.states.dc.property_tax

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_dc_property_tax_credit()
    else:
        return None


dc_property_tax_credit = create_dc_property_tax_credit_reform(
    None, None, bypass=True
)
