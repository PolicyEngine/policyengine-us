from policyengine_us.model_api import *


class living_arrangements_allow_for_food_preparation(Variable):
    value_type = bool
    entity = Household
    label = "Living arrangements allow for food preparation"
    documentation = (
        "Whether the household's living arrangement lets its members prepare "
        "meals at home, with adequate cooking and food storage facilities. "
        "Defaults to true, the common case; set it to false for a household "
        "without such facilities, such as a room without a kitchen. California "
        "pays the SSI/SSP restaurant meals allowance only to an aged or disabled "
        "recipient whose living arrangement prevents meal preparation at home."
    )
    definition_period = YEAR
    default_value = True
    reference = [
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415140SF",
    ]
