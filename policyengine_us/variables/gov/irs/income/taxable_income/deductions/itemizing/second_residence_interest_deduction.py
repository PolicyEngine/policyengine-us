from policyengine_us.model_api import *


class second_residence_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Interest deduction attributable to a second residence"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The part of the federal interest deduction that comes from home "
        "mortgage interest, points and qualified mortgage insurance premiums "
        "on the second qualified residence. Interest and points take the "
        "deductible share of the pooled mortgage interest and points under "
        "the acquisition-debt limit; premiums take the adjusted-gross-income "
        "phase-out that applies to all premiums."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#h_3",
        "https://www.law.cornell.edu/uscode/text/26/163#h_4_A",
        "https://www.irs.gov/pub/irs-pdf/p936.pdf#page=16",
    ]

    def formula(tax_unit, period, parameters):
        second_residence_pool = add(
            tax_unit,
            period,
            ["second_residence_mortgage_interest", "second_residence_mortgage_points"],
        )
        pool = tax_unit("home_mortgage_interest_tax_unit", period) + add(
            tax_unit,
            period,
            ["home_mortgage_points", "second_residence_mortgage_points"],
        )
        deductible_pool = tax_unit("deductible_mortgage_interest_tax_unit", period)
        pool_share = np.divide(
            second_residence_pool,
            pool,
            out=np.zeros_like(pool),
            where=pool > 0,
        )
        second_residence_premiums = add(
            tax_unit, period, ["second_residence_mortgage_insurance_premiums"]
        )
        premiums = second_residence_premiums + add(
            tax_unit, period, ["mortgage_insurance_premiums"]
        )
        deductible_premiums = tax_unit("deductible_mortgage_insurance_premiums", period)
        premium_share = np.divide(
            second_residence_premiums,
            premiums,
            out=np.zeros_like(premiums),
            where=premiums > 0,
        )
        return deductible_pool * pool_share + deductible_premiums * premium_share
