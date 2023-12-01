from policyengine_us.model_api import *


class mo_net_state_income_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri net state income taxes"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf#page=2",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.141&bid=7212",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # follows Form MO-A Part II and Part II worksheet logic:

        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.itemized
        salt_cap = p.salt_and_real_estate.cap[filing_status]

        uncapped_itax = max_(0, add(tax_unit, period, ["state_income_tax"]))
        uncapped_ptax = add(tax_unit, period, ["real_estate_taxes"])
        uncapped_salt = uncapped_itax + uncapped_ptax

        ratio = np.zeros_like(uncapped_salt)
        mask = uncapped_salt != 0
        ratio[mask] = uncapped_itax[mask] / uncapped_salt[mask]

        return where(uncapped_salt > salt_cap, salt_cap * ratio, uncapped_itax)
