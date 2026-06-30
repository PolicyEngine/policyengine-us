from policyengine_us.model_api import *


class NMCCAPServiceUnit(Enum):
    FULL_TIME = "Full time (30+ hrs/wk)"
    PART_TIME_1 = "Part time 1 (8-29 hrs/wk)"
    PART_TIME_2 = "Part time 2 (split custody, 8-19 hrs/wk)"
    PART_TIME_3 = "Part time 3 (<=7 hrs/wk)"


class nm_ccap_service_unit(Variable):
    value_type = Enum
    entity = Person
    possible_values = NMCCAPServiceUnit
    default_value = NMCCAPServiceUnit.FULL_TIME
    definition_period = MONTH
    label = "New Mexico CCAP service unit"
    defined_for = StateCode.NM
    reference = "https://www.nmececd.org/wp-content/uploads/2024/05/Cost-Model-Reimbursement-Rate-Flyer-English-and-Spanish-Revised-May-2024.pdf#page=1"

    def formula(person, period, parameters):
        # The hours bracket maps average weekly care hours to FULL_TIME,
        # PART_TIME_1, or PART_TIME_3. PART_TIME_2 (split custody / two
        # providers) is not derivable from hours alone, so it is never
        # produced by this formula; we don't track custody arrangements at the
        # moment.
        # childcare_hours_per_week is a weekly rate stored annually; read it
        # with period.this_year so it is not auto-divided to a monthly value.
        hours = person("childcare_hours_per_week", period.this_year)
        p = parameters(period).gov.states.nm.ececd.ccap.rates.service_unit
        return p.hours.calc(hours)
