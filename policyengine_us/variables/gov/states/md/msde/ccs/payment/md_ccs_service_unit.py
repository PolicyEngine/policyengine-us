from policyengine_us.model_api import *


class MDCCSServiceUnit(Enum):
    UNIT_1 = "1 Unit (3 hours or less per day)"
    UNIT_2 = "2 Units (more than 3 to less than 6 hours per day)"
    UNIT_3 = "3 Units (6 or more hours per day)"


class md_ccs_service_unit(Variable):
    value_type = Enum
    entity = Person
    possible_values = MDCCSServiceUnit
    default_value = MDCCSServiceUnit.UNIT_3
    definition_period = MONTH
    defined_for = StateCode.MD
    label = "Maryland CCS service unit category"
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.02",
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.11",
    )

    def formula(person, period, parameters):
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        p = parameters(period).gov.states.md.msde.ccs.copay
        units = p.unit_hours.calc(hours_per_day)
        # COMAR 13A.14.06.02B(59): one unit is 3 hours or less per day, two
        # units more than 3 but less than 6, three units 6 or more. The
        # bracket returns 0 for negative or NaN hours, which no unit matches;
        # without an explicit default numpy's select would fill those rows
        # with the integer 0, which cannot be encoded as an MDCCSServiceUnit.
        # Anything at or below the one-unit ceiling, including out-of-range
        # hours, is one unit, matching how zero hours is already treated.
        return select(
            [units == 3, units == 2],
            [MDCCSServiceUnit.UNIT_3, MDCCSServiceUnit.UNIT_2],
            default=MDCCSServiceUnit.UNIT_1,
        )
