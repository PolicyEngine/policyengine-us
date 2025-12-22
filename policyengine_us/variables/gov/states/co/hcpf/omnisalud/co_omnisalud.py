from policyengine_us.model_api import *


class co_omnisalud(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado OmniSalud premium subsidy"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://connectforhealthco.com/get-started/omnisalud/",
        "https://coloradoimmigrant.org/wp-content/uploads/2024/03/Eng.-OmniSalud-Guide-2024.pdf",
    ]
    documentation = """
    Colorado OmniSalud provides a premium subsidy (SilverEnhanced Savings)
    that covers the full cost of health insurance premiums for eligible
    individuals, resulting in $0 monthly premium.

    The benefit value is equal to the second lowest cost silver plan (SLCSP)
    premium, similar to the federal ACA premium tax credit.
    """

    def formula(tax_unit, period, parameters):
        # Check if anyone in the tax unit is eligible
        eligible = tax_unit.any(
            tax_unit.members("co_omnisalud_eligible", period)
        )

        # The subsidy covers the full premium (SLCSP)
        # Sum monthly SLCSP to get annual amount
        slcsp_monthly = tax_unit("slcsp", period)

        return where(eligible, slcsp_monthly * MONTHS_IN_YEAR, 0)
