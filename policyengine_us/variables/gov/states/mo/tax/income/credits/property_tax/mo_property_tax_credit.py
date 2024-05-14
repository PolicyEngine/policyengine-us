from policyengine_us.model_api import *


class mo_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439",
    )
    defined_for = "mo_ptc_taxunit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mo.tax.income.credits.property_tax
        # compute maximum (that is, pre-phaseout) credit amount for rent
        rent = add(tax_unit, period, ["rent"])
        ratio = p.property_tax_rent_ratio
        rent_limit = p.rent_property_tax_limit
        rent_amount = min_(rent * ratio, rent_limit)
        # compute maximum (that is, pre-phaseout) credit amount for taxes
        ptax = add(tax_unit, period, ["real_estate_taxes"])
        ptax_limit = p.property_tax_limit
        ptax_amount = min_(ptax, ptax_limit)
        # combine the rent_amount and ptax_amount subject to ptax_limit
        max_credit = min_(rent_amount + ptax_amount, ptax_limit)
        # phase out credit amount using legislative formula (not form table)
        po_start = p.phase_out.threshold
        po_step = p.phase_out.step
        po_rate = p.phase_out.rate
        net_income = tax_unit("mo_ptc_net_income", period)
        excess_income = max_(0, net_income - po_start)
        po_steps = np.ceil(excess_income / po_step)
        phaseout_amount = po_rate * po_steps * net_income
        return max_(0, max_credit - phaseout_amount)
