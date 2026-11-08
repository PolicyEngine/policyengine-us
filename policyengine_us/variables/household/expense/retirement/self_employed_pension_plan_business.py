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
        "which gives the largest limit under one dollar limit; a business "
        "with a net loss is left out. The person then chooses how much to "
        "contribute to each plan, and Form 7206 line 9 for the business under "
        "which the health insurance plan is established takes the least that "
        "this business's plan must carry: the part of the plan deduction "
        "above what the other plans can carry, which is their earned income "
        "or, if less, their employers' limits on employer contributions plus "
        "the person's elective deferral room. A named business limits "
        "the deduction to that business's earned income, as when the person "
        "has more than one business but only one has a plan. The input "
        "cannot name two of the three businesses."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/404#a_8_C",
        "https://www.law.cornell.edu/uscode/text/26/401#c_4",
        # PDF pages 7, 39: with more than one business but only one plan,
        # only that business's earned income counts; a sole proprietor is
        # their own employer, and a partnership is each partner's employer;
        # Deduction Worksheet step 1 takes Schedule C, Schedule F or K-1 box
        # 14 code A.
        "https://www.irs.gov/pub/irs-prior/p560--2025.pdf#page=7",
    )
