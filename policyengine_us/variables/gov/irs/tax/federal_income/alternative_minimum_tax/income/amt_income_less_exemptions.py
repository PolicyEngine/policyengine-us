from policyengine_us.model_api import *


class amt_income_less_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax Income less exemptions"
    unit = USD
    documentation = (
        "AMT income less the exemption, including the limited child exemption "
        "under IRC 59(j) before 2018."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/55#b_1_B",
        "https://www.law.cornell.edu/uscode/text/26/59#j",
        "https://www.law.cornell.edu/uscode/text/26/55#d_4_A_iii",
        "https://www.irs.gov/pub/irs-prior/i6251--2017.pdf#page=10",
        "https://www.irs.gov/pub/irs-pdf/i6251.pdf#page=9",
    ]

    def formula(tax_unit, period, parameters):
        # Form 6251, Part I
        # Line 4
        amt_income = tax_unit("amt_income", period)

        # Form 6251, Part II top
        # Line 5
        amt_exemption = tax_unit("amt_exemption", period)

        # Line 6 (2017 lines 28-30): IRC 59(j) limits only the exemption,
        # not the AMTI base. amt_exemption applies that cap before 2018.
        return max_(0, amt_income - amt_exemption)
