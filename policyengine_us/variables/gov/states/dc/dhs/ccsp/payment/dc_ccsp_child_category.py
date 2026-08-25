from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.dc.dhs.ccsp.payment.dc_ccsp_age_category import (
    DCCCSPAgeCategory,
)


class DCCCSPChildCategory(Enum):
    INFANT_AND_TODDLER = "Infant and Toddler"
    INFANT_AND_TODDLER_SPECIAL_NEEDS = "Infant and Toddler Special Needs"
    PRESCHOOL = "Preschool"
    PRESCHOOL_BEFORE_AND_AFTER = "Preschool Before and After"
    SCHOOL_AGE_BEFORE_AND_AFTER = "School-Age Before and After"
    SCHOOL_AGE_BEFORE_OR_AFTER = "School-Age Before or After"
    PRESCHOOL_AND_SCHOOL_AGE_SPECIAL_NEEDS = "Preschool and School-Age Special Needs"


class dc_ccsp_child_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = DCCCSPChildCategory
    default_value = DCCCSPChildCategory.PRESCHOOL
    label = "DC Child Care Subsidy Program (CCSP) child category"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf"

    def formula(person, period, parameters):
        # The reimbursement rate sheet fuses the age band with the service
        # authorized, so this maps the age band onto the row it determines.
        # Four of the seven rows are never produced from household inputs and
        # are reached only by setting this variable directly:
        #
        #   INFANT_AND_TODDLER_SPECIAL_NEEDS
        #   PRESCHOOL_AND_SCHOOL_AGE_SPECIAL_NEEDS
        #     The special needs rate is authorized at the facility, not the
        #     child. Under the Level I subsidy agreement a provider must file a
        #     Special Needs Rate Request Form per facility and renew it
        #     annually, so no household characteristic implies it. It is
        #     deliberately not derived from is_disabled, which describes the
        #     child rather than the provider's authorization.
        #
        #   PRESCHOOL_BEFORE_AND_AFTER
        #     Whether a preschooler needs wraparound care around a public
        #     pre-kindergarten day is not in the household data. It carries the
        #     same rate as PRESCHOOL wherever both are published, so the plain
        #     row is used.
        #
        #   SCHOOL_AGE_BEFORE_AND_AFTER
        #     Care on both ends of the school day. Whether a school-age child
        #     needs one end or both is not in the household data, and care on a
        #     single end is the more common placement, so the school-age band
        #     maps to SCHOOL_AGE_BEFORE_OR_AFTER below.
        #
        # The rate sheet publishes no plain school-age row, because school-age
        # children may participate only for out-of-school-time care, so every
        # school-age placement is before or after school care by definition.
        # SCHOOL_AGE_BEFORE_OR_AFTER is priced only in the two traditional
        # columns, so a school-age child whose schedule type is set to an
        # extended day or nontraditional column reaches no published rate. Set
        # this variable to SCHOOL_AGE_BEFORE_AND_AFTER for those placements.
        age_category = person("dc_ccsp_age_category", period)
        return select(
            [
                age_category == DCCCSPAgeCategory.INFANT_AND_TODDLER,
                age_category == DCCCSPAgeCategory.PRESCHOOL,
            ],
            [
                DCCCSPChildCategory.INFANT_AND_TODDLER,
                DCCCSPChildCategory.PRESCHOOL,
            ],
            # The remaining band is school-age.
            default=DCCCSPChildCategory.SCHOOL_AGE_BEFORE_OR_AFTER,
        )
