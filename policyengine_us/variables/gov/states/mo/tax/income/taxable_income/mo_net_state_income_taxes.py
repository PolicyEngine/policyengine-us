from policyengine_us.model_api import *
from policyengine_us.tools.period_branch import has_input


class mo_net_state_income_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri net state income taxes"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf#page=2",
        "https://dor.mo.gov/forms/MO-A_2025.pdf#page=2",
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

    def formula_2025(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        if has_input(simulation, "state_and_local_sales_or_income_tax", period) and (
            not has_input(simulation, "state_and_local_sales_tax_elected", period)
        ):
            # Older callers may supply only a placeholder Schedule A amount.
            return mo_net_state_income_taxes.formula(tax_unit, period, parameters)

        elects_sales_tax = tax_unit("state_and_local_sales_tax_elected", period)
        line_5a = tax_unit("state_and_local_sales_or_income_tax", period)
        earnings_taxes = add(
            tax_unit,
            period,
            ["mo_kansas_city_earnings_tax", "mo_st_louis_earnings_tax"],
        )
        # MO-A Part 2 line 10 excludes city earnings taxes from the addback.
        # The worksheet denominator includes all federal Schedule A line 5d.
        net_income_tax = where(elects_sales_tax, 0, max_(line_5a - earnings_taxes, 0))
        gross_salt = tax_unit("salt", period)
        deducted_salt = tax_unit("salt_deduction", period)
        income_tax_share = np.divide(
            net_income_tax,
            gross_salt,
            out=np.zeros_like(gross_salt),
            where=gross_salt > 0,
        )
        return deducted_salt * income_tax_share
