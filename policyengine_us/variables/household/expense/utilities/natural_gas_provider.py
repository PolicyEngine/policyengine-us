from policyengine_us.model_api import *
from policyengine_us.tools.utility_providers import NaturalGasProvider


class natural_gas_provider(Variable):
    value_type = Enum
    possible_values = NaturalGasProvider
    default_value = NaturalGasProvider.UNSPECIFIED
    entity = SPMUnit
    definition_period = YEAR
    label = "Natural gas utility provider"
    documentation = (
        "Company providing the home's natural gas distribution service, as named "
        "on the utility bill. Report the distribution utility even when a "
        "separate retailer supplies the gas. UNSPECIFIED means the company was "
        "not reported; OTHER means a reported company outside the listed choices. "
        "Named companies support Idaho, Illinois and Rhode Island heating "
        "assistance. The state mapping includes their service in other states. "
        "Electricity and gas companies are reported independently. "
        "This input does not imply program enrollment or bill receipt."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://webserver.rilegislature.gov/Statutes/TITLE39/39-1/39-1-27.12.htm",
        # Form EIA-176, 2024, residential customers by reporting company and state.
        "https://www.eia.gov/naturalgas/ngqs/",
        # Illinois distribution companies, including Peoples Gas Light & Coke.
        "https://icc.illinois.gov/public-utility",
        # Avista Utilities, Form 10-K, Part I, Item 1 (electric and gas territories).
        "https://www.sec.gov/Archives/edgar/data/104918/000119312526067872/ava-20251231.htm",
        "https://www.intgas.com/in-the-community/about-us/",
        "https://ripuc.ri.gov/utility-information/regulated-utilities",
    )
