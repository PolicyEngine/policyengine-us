from policyengine_us.model_api import *


class vt_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Vermont Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://legislature.vermont.gov/statutes/section/33/018/01812",
        "https://info.healthconnect.vermont.gov/financial-help",
    )
    documentation = (
        "A tax unit is eligible for Vermont Premium Assistance when the program "
        "is in effect, at least one member is eligible for the federal ACA "
        "premium tax credit (which embeds on-Marketplace enrollment, the "
        "married-filing-separately exclusion, and the federal required-"
        "contribution income test), and household income is at or below 300% of "
        "the federal poverty line, measured as the exact ratio of ACA MAGI to "
        "the prior-year guideline rather than the truncated aca_magi_fraction. "
        "Vermont imposes no minimum-income floor, so "
        "the low end is governed by the federal PTC gate, including its below-"
        "poverty immigration exception, which Vermont inherits rather than "
        "overrides."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.dvha.premium_assistance
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC.
        aptc_eligible = tax_unit.any(tax_unit.members("is_aca_ptc_eligible", period))
        # 33 V.S.A. 1812(a)(1) covers income "less than or equal to 300
        # percent of federal poverty level". Test the exact ratio, not the
        # truncated aca_magi_fraction: truncation maps 300.00%-300.99% to
        # 3.00, which would admit incomes above 300%.
        magi = max_(tax_unit("aca_magi", period), 0)
        exact_magi_frac = magi / tax_unit("tax_unit_fpg", period.last_year)
        income_eligible = exact_magi_frac <= p.fpl_limit
        return in_effect & aptc_eligible & income_eligible
