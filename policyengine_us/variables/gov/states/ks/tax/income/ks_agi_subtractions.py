from policyengine_us.model_api import *


class ks_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://ksrevisor.gov/statutes/chapters/ch79/079_032_0117.html",
        "https://www.ksrevenue.gov/pdf/ip25.pdf#page=12",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        # Dependents' income is not in federal AGI; they report it on their
        # own return, so only the head's and spouse's amounts are subtracted.
        agi = tax_unit("adjusted_gross_income", period)
        taxable_oasdi = add(tax_unit, period, ["taxable_social_security"])
        p = parameters(period).gov.states.ks.tax.income.agi.subtractions
        oasdi_subtraction = where(agi <= p.oasdi.agi_limit, taxable_oasdi, 0)
        us_govt_interest = add(tax_unit, period, ["us_govt_interest"])
        plan_529 = tax_unit("ks_529_plan_subtraction", period)
        # K.S.A. 79-32,117(c)(v) / Form K-40 Schedule S Line A12
        salt_refund_income = tax_unit_non_dep_sum(
            "salt_refund_income", tax_unit, period
        )
        # K.S.A. § 79-32,117(c)(ii), (vii)–(ix) / Form K-40 Schedule S Line A13
        # Kansas exempts KPERS, Kansas police/firemen, Kansas judges, federal civil service,
        # military retirement pay, and military survivor benefits (10 U.S.C. 1450).
        # Out-of-state public pensions are not exempt. PolicyEngine models this by subtracting
        # taxable_public_pension_income as an in-state proxy, plus military retirement pay and survivors.
        public_and_military_pension = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "taxable_public_pension_income",
                "military_retirement_income",
            ],
        )
        return (
            oasdi_subtraction
            + us_govt_interest
            + plan_529
            + salt_refund_income
            + public_and_military_pension
            + tax_unit("ks_other_subtractions", period)
        )
