from policyengine_us.model_api import *
from policyengine_us.tools.utility_providers import ElectricityProvider


class electricity_provider(Variable):
    value_type = Enum
    possible_values = ElectricityProvider
    default_value = ElectricityProvider.UNSPECIFIED
    entity = SPMUnit
    definition_period = YEAR
    label = "Electricity utility provider"
    documentation = (
        "Company providing the home's electric distribution service, as named on "
        "the utility bill. Report the distribution utility even when a separate "
        "retailer supplies the energy. UNSPECIFIED means the company was not "
        "reported; OTHER means a reported company outside the listed choices. "
        "Named companies support Idaho, Illinois and Rhode Island heating "
        "assistance. The state mapping includes their service in other states. "
        "This input does not imply program enrollment or bill receipt."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://webserver.rilegislature.gov/Statutes/TITLE39/39-1/39-1-27.12.htm",
        "https://oemr.idaho.gov/utilities/",
        # Form EIA-861, 2025 final, Service_Territory_2025 (utility by county).
        "https://www.eia.gov/electricity/data/eia861/",
        # EIA lists PacifiCorp as a whole. This is its Rocky Mountain Power brand.
        "https://www.rockymountainpower.net/about.html",
    )
