from policyengine_us.model_api import add


def ga_liheap_has_direct_payment_route(spm_unit, period):
    """Identify unsubsidized rent that includes all utilities.

    Georgia's manual energy-burden table (physical page 89) permits payment
    directly to these renters. The rental agreement is assumed verified.
    https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=89
    """
    return (
        spm_unit("heat_expense_included_in_rent", period)
        & ~spm_unit.household("tenant_pays_utilities", period)
        & (add(spm_unit, period, ["rent"]) > 0)
        & ~spm_unit("receives_housing_assistance", period)
        & ~spm_unit.household("is_in_public_housing", period)
    )
