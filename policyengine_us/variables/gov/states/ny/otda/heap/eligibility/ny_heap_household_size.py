from policyengine_us.model_api import *


class ny_heap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP qualified household size"
    defined_for = StateCode.NY
    # Chapter 8 D.4 and D.9, PDF pages 34, 36, 37, 44.
    reference = ("https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=34",)
    documentation = (
        "SPM members who are citizens or federally qualified noncitizens. Nonqualified "
        "members' income still counts in full. Foster members and federal Code C SSI "
        "recipients are excluded using existing inputs. Roomers, employees and fleeing "
        "felons remain unsupported. The existing immigration enum does not separately "
        "identify every additional federally protected status."
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        included = ~person("ny_heap_is_excluded_person", period)
        qualified = person("is_citizen_or_legal_immigrant", period)
        return spm_unit.sum(included & qualified)
