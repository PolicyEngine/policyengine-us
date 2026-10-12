from policyengine_us.model_api import *


class va_ag_is_joint_initial_month(Variable):
    value_type = bool
    entity = Person
    label = "Virginia Auxiliary Grant couple in the initial month"
    definition_period = MONTH
    default_value = False
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf"
    documentation = """Set for both spouses only in the initial application month when both lived together at the start of the month, entered approved care, applied, and were found eligible that month. Later institutional months are separate cases; reflect that in the federal SSI claim inputs too."""
