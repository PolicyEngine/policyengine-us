from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_vt_fair_share() -> Reform:
    class vt_fair_share_surcharge(Variable):
        value_type = float
        entity = TaxUnit
        label = "Vermont H.794 high-income surcharge"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.VT
        reference = (
            # PDF pages 2-3, 14
            "https://legislature.vermont.gov/Documents/2026/Docs/BILLS/H-0794/H-0794%20As%20Introduced.pdf#page=2",
            # PDF pages 2, 14
            "https://legislature.vermont.gov/Documents/2026/Docs/BILLS/S-0282/S-0282%20As%20Introduced.pdf#page=2",
            "https://fairsharevt.org/revenue-proposals-tax-cuts",
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.vt.fair_share
            # 32 V.S.A. § 5822a(a)-(c) as drafted: the base is the federal AGI
            # of the return, with one threshold schedule for every filing status.
            agi = max_(tax_unit("adjusted_gross_income", period), 0)
            return where(p.in_effect, p.rate.calc(agi), 0)

    # Mirrors policyengine_us/variables/gov/states/vt/tax/income/
    # vt_income_tax_before_refundable_credits.py plus the surcharge; keep the
    # two formulas in sync when the baseline changes.
    class vt_income_tax_before_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Vermont income tax before refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.VT
        reference = (
            "https://legislature.vermont.gov/Documents/2026/Docs/BILLS/H-0794/H-0794%20As%20Introduced.pdf#page=2",
            "https://legislature.vermont.gov/statutes/section/32/151/05822",
        )

        def formula(tax_unit, period, parameters):
            itax_before_credits = tax_unit(
                "vt_income_tax_before_non_refundable_credits", period
            )
            non_refundable_credits = tax_unit("vt_non_refundable_credits", period)
            tax_after_non_refundable_credits = max_(
                0, itax_before_credits - non_refundable_credits
            )
            # § 5822a(a)-(b): the surcharge is in addition to any tax assessed
            # under chapter 151, so it is added after the non-refundable credits,
            # which apply against the § 5822 tax, and outside the § 5822(a)(6)
            # comparison with 3% of federal AGI.
            surcharge = tax_unit("vt_fair_share_surcharge", period)
            return tax_after_non_refundable_credits + surcharge

    class reform(Reform):
        def apply(self):
            self.update_variable(vt_fair_share_surcharge)
            self.update_variable(vt_income_tax_before_refundable_credits)

    return reform


def create_vt_fair_share_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_vt_fair_share()

    p = parameters.gov.contrib.states.vt.fair_share

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_vt_fair_share()
    else:
        return None


vt_fair_share = create_vt_fair_share_reform(None, None, bypass=True)
