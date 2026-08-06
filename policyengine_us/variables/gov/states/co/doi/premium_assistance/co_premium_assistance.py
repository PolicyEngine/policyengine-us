from policyengine_us.model_api import *


class co_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = (
        "https://connectforhealthco.com/financial-help/colorado-premium-assistance/"
    )
    documentation = (
        "Colorado state flat premium wrap on top of the federal ACA premium "
        "tax credit, administered by Connect for Health Colorado and funded by "
        "the Health Insurance Affordability Enterprise. The monthly amount is a "
        "flat build-up: a first-member amount plus an additional-member amount "
        "for each further member, counting at most the member cap. The annual "
        "amount is twelve times the monthly amount, capped at the remaining "
        "premium after the federal credit. This uses three approximations: the "
        "enrolled-plan premium is approximated by the benchmark SLCSP (the "
        "residual cap is SLCSP minus the federal PTC, floored at zero); the "
        "count of members with a remaining premium is approximated by the "
        "count of members eligible for the federal ACA PTC; and full-year "
        "enrollment is assumed via the times-twelve annualization. Colorado "
        "Premium Assistance is paid upfront and is not a tax credit, so no "
        "reconciliation or tax-return interaction is modeled."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.doi.premium_assistance
        # Count members with a remaining premium, approximated by members
        # eligible for the federal ACA PTC, capped at the member cap.
        n = min_(
            add(tax_unit, period, ["is_aca_ptc_eligible"]),
            p.member_cap,
        )
        flat_monthly = where(
            n > 0,
            p.amount.first_member + p.amount.additional_member * (n - 1),
            0,
        )
        # slcsp is a MONTH-period variable; core sums the 12 months when called
        # from this YEAR formula. Approximates the enrolled-plan premium.
        slcsp_annual = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        residual = max_(0, slcsp_annual - aca_ptc)
        annual = min_(MONTHS_IN_YEAR * flat_monthly, residual)
        eligible = tax_unit("co_premium_assistance_eligible", period)
        return where(eligible, annual, 0)
