from policyengine_us.model_api import *


def create_ny_a06774_enhanced_cdcc() -> Reform:
    """
    NY Assembly Bill A06774 - Enhanced Child and Dependent Care Credit

    Increases the NY child and dependent care credit to 110% of the federal
    credit for taxpayers with NY adjusted gross income up to $50,000.

    Reference: https://www.nysenate.gov/legislation/bills/2025/A6774
    """

    class ny_cdcc(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY CDCC"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.nysenate.gov/legislation/bills/2025/A6774",
            "https://www.nysenate.gov/legislation/laws/TAX/606",
        )
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ny.a06774
            ny_agi = tax_unit("ny_agi", period)
            income_threshold = p.income_threshold
            # Calculate the enhanced credit (110% of federal CDCC)
            federal_cdcc = tax_unit("cdcc", period)
            enhanced_cdcc = federal_cdcc * p.match

            # Calculate the standard NY CDCC
            cdcc_max = tax_unit("ny_cdcc_max", period)
            expenses = tax_unit("cdcc_relevant_expenses", period)
            ny_rate = tax_unit("ny_cdcc_rate", period)
            federal_rate = tax_unit("cdcc_rate", period)
            standard_ny_cdcc = min_(
                cdcc_max, expenses * ny_rate * federal_rate
            )

            # Use enhanced credit if reform is in effect and income is
            # at or below the threshold
            eligible_for_enhanced = ny_agi <= income_threshold
            return where(
                eligible_for_enhanced, enhanced_cdcc, standard_ny_cdcc
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_cdcc)

    return reform


def create_ny_a06774_enhanced_cdcc_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ny_a06774_enhanced_cdcc()

    p = parameters(period).gov.contrib.states.ny.a06774

    if p.in_effect:
        return create_ny_a06774_enhanced_cdcc()
    else:
        return None


ny_a06774_enhanced_cdcc = create_ny_a06774_enhanced_cdcc_reform(
    None, None, bypass=True
)
