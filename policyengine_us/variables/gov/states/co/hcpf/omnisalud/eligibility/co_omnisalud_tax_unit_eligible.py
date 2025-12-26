from policyengine_us.model_api import *


class co_omnisalud_tax_unit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tax unit eligible for Colorado OmniSalud"
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = [
        "https://connectforhealthco.com/get-started/omnisalud/",
        "https://coloradoimmigrant.org/wp-content/uploads/2024/03/Eng.-OmniSalud-Guide-2024.pdf",
    ]
    documentation = """
    A tax unit is eligible for Colorado OmniSalud if any member is eligible.
    """

    def formula(tax_unit, period, parameters):
        return tax_unit.any(tax_unit.members("co_omnisalud_eligible", period))
