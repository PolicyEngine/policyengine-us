from policyengine_us.model_api import *


# PolicyEngine does not record the service of the deceased retired member
# whose Survivor Benefit Plan annuity a person receives, so this is an input.
class nc_military_retirement_survivor_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina military retirement deduction eligible as a Survivor Benefit Plan beneficiary"
    documentation = (
        "Whether this person receives Survivor Benefit Plan (10 U.S.C. 1447) "
        "payments as the beneficiary of a retired member who served at least "
        "20 years in the uniformed services or was medically retired under "
        "10 U.S.C. Chapter 61. Record survivor benefits in "
        "military_retirement_pay_survivors when this person also receives "
        "their own military retirement pay; military_retirement_pay then "
        "contains only their own pay, which must independently qualify. "
        "In that case, supply the recipient's years_in_military or "
        "is_permanently_disabled_veteran record: setting the combined "
        "nc_military_retirement_deduction_eligible input to true alone "
        "does not establish eligibility for their own pay. "
        "If military_retirement_pay_survivors is zero, this flag also allows "
        "military_retirement_pay to contain qualifying survivor benefits. "
        "Do not record the same survivor benefits in both income inputs."
    )
    definition_period = YEAR
    reference = (
        # G.S. 105-153.5(b)(5a)b.
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/filing-topics/military-retirement",
    )
