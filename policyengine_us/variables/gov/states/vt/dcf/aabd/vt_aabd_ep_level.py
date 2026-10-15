from policyengine_us.model_api import *


class VTAABDEssentialPersonLevel(Enum):
    FULL = "Certified full Essential Person care level"
    PARTIAL_67 = "Certified 67 percent Essential Person care level"
    PARTIAL_34 = "Certified 34 percent Essential Person care level"
    NONE = "No certified Essential Person arrangement"


class vt_aabd_ep_level(Variable):
    value_type = Enum
    entity = Person
    label = "Vermont certified Essential Person care level"
    definition_period = MONTH
    possible_values = VTAABDEssentialPersonLevel
    default_value = VTAABDEssentialPersonLevel.NONE
    # PDF pages 38, 40-41, 44
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=38"
    documentation = """
    Certified co-resident essential person under rules 2781-2784: full for
    an ineligible spouse 55 or older, or required personal care, or seven
    homemaker services; 67 percent for a younger spouse unable to work who
    provides qualifying care, or a nonspouse providing four to six services;
    34 percent for a nonspouse providing one to three services. Certification
    includes benefit pursuit and care preventing institutionalization. Set it
    on the aged, blind or disabled recipient, not on the essential person; for
    an eligible couple, set it on either spouse and the couple's grant uses the
    highest level set on either spouse.
    """
