from policyengine_us.model_api import *


class ssi_resource_deeming_temporary_absence(Variable):
    value_type = bool
    entity = Person
    label = "Temporary absence retaining SSI deeming household membership"
    definition_period = MONTH
    reference = "https://www.ecfr.gov/current/title-20/section-416.1167"
    documentation = """
    Adjudicated SSI household membership during a temporary absence under
    416.1167. The tax unit and marital unit must still represent that SSI
    household. Includes absence with intended and actual return in the same
    or next month; medical-facility absence while 416.212 benefits are payable
    (including the specified discharge extension); children away at school
    subject to parental control; and active-duty absence without contrary
    evidence. For active-duty contrary evidence, deeming ceases the following
    month under 416.1167(c). Set this monthly determination accordingly; actual
    return dates, 416.212 awards and contrary evidence are not model inputs.
    """
