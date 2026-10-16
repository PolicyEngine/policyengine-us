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
    utility bill is in their name", so this route ignores subsidy status and
    tenant_pays_utilities: a positive electric bill is the utility-bill
    documentation. Page 82's ineligibility when "the rent includes utilities"
    is read as rent covering every utility, which a separate electric bill
    rules out. Unsubsidized renters whose rent includes all utilities take
    the direct-payment route's lowest award instead. The FY2024 matrix note
    ("The main fuel type is not always where the benefit is applied") pays
    the main-fuel amount when the benefit goes to the electric bill. The
    pre-subsidy bill matches heating_expense and avoids the
    program-dependent subsidies in electricity_expense.
    Manual pages 4, 82 and 89:
    https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=4
    FY2024 matrix:
    https://liheapch.acf.gov/docs/2024/benefits-matricies/GA_BenefitMatrix_2024.pdf
    """
    return (
        spm_unit("heat_expense_included_in_rent", period)
        & (add(spm_unit, period, ["rent"]) > 0)
        & (spm_unit("pre_subsidy_electricity_expense", period) > 0)
    )
