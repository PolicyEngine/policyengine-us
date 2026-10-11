from policyengine_us.model_api import *


class SelfEmployedPensionPlanBusiness(Enum):
    SCHEDULE_C = "Schedule C business"
    SCHEDULE_F = "Schedule F farm"
    PARTNERSHIP = "Partnership"
    ALL = "All self-employment businesses"


class self_employed_pension_plan_business(Variable):
    value_type = Enum
    entity = Person
    possible_values = SelfEmployedPensionPlanBusiness
    default_value = SelfEmployedPensionPlanBusiness.ALL
    definition_period = YEAR
    label = "Business under which the self-employed retirement plan is established"
    documentation = (
        "The trade or business under which the person's SEP, SIMPLE or "
        "qualified plan (Schedule 1 line 16) is established: the Schedule C "
        "business, the Schedule F farm, or a partnership in which the person "
        "has Schedule K-1 box 14 code A net earnings. The plan deduction is "
        "limited to earned income from the plan's business. ALL (the default) "
        "means every one of these businesses with a net profit has a plan, "
        "which is the largest limit the person's businesses allow; a "
        "business with a net loss is left out. A named business limits the "
        "deduction to that business's earned income, as when the person has "
        "more than one business but only one has a plan."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/404#a_8_C",
        "https://www.law.cornell.edu/uscode/text/26/401#c_4",
        # Compensation: with more than one business but only one plan, only
        # that business's earned income counts. Employer: a sole proprietor
        # is its own employer, and a partnership is each partner's employer.
        "https://www.irs.gov/pub/irs-pdf/p560.pdf#page=7",
        # Deduction Worksheet step 1: Schedule C, Schedule F or K-1 box 14 A.
        "https://www.irs.gov/pub/irs-pdf/p560.pdf#page=39",
    )
