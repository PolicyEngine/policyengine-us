from policyengine_us.model_api import *


class co_omnisalud(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado OmniSalud premium subsidy"
    unit = USD
    definition_period = YEAR
    defined_for = "co_omnisalud_tax_unit_eligible"
    adds = ["slcsp"]
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
