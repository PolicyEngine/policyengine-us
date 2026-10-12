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
        # Missouri adds back the state and local income tax actually included
        # in the federal itemized SALT deduction. The base is therefore the
        # federal SALT cap *after* the OBBBA income-based phase-down (the
        # salt_cap variable), not the static base cap
        # p.salt_and_real_estate.cap, which would otherwise over-state the
        # add-back for high earners whose federal SALT has phased down to the
        # $10,000 floor.
        salt_cap = tax_unit("salt_cap", period)

        uncapped_itax = max_(0, add(tax_unit, period, ["state_withheld_income_tax"]))
        uncapped_ptax = add(tax_unit, period, ["real_estate_taxes"])
        uncapped_salt = uncapped_itax + uncapped_ptax

        ratio = np.zeros_like(uncapped_salt)
        mask = uncapped_salt != 0
        ratio[mask] = uncapped_itax[mask] / uncapped_salt[mask]

        # Pro-rate the income-tax share against the SALT actually deducted
        # federally after the phase-down (MO-A Part 2 worksheet).
        return where(uncapped_salt > salt_cap, salt_cap * ratio, uncapped_itax)
