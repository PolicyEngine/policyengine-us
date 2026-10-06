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


def ga_liheap_has_electric_vendor_route(spm_unit, period):
    """Identify heat-in-rent renters billed directly for electric.

    Georgia's manual energy-burden table (physical page 89, third row) gives
    unsubsidized renters with heat in rent and their own electric bill an
    energy burden, "Paid to electric vendor because gas usage is
    indeterminate". Page 4 makes subsidized renters eligible when "their
    utility bill is in their name", so this route ignores subsidy status;
    subsidized heat-in-rent renters without a bill stay ineligible.
    tenant_pays_utilities separates these renters from the rows where all
    utilities are in rent, and a positive electric bill is the utility-bill
    documentation. The pre-subsidy bill matches heating_expense and avoids
    the program-dependent subsidies in electricity_expense.
    Manual pages 4 and 89:
    https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=89
    """
    return (
        spm_unit("heat_expense_included_in_rent", period)
        & spm_unit.household("tenant_pays_utilities", period)
        & (add(spm_unit, period, ["rent"]) > 0)
        & (spm_unit("pre_subsidy_electricity_expense", period) > 0)
    )
