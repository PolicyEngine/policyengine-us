from policyengine_us.model_api import *


class mt_military_retirement_exemption_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the residency and timing conditions of the Montana military retirement exemption"
    definition_period = YEAR
    default_value = True
    documentation = (
        "MCA 15-30-2120(9): the retiree or survivor became a Montana resident on "
        "or after June 30, 2023, or lived in Montana before the military "
        "retirement pay or survivor benefits began; claims the exemption "
        "within five consecutive years of meeting that condition (tax years "
        "2024 through 2028 for residents from before July 2023); and has not "
        "claimed it before moving out of Montana. Set this to false for a "
        "filer who fails any of these conditions."
    )
    reference = (
        "https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://revenue.mt.gov/files/Forms/Montana-Working-Military-Retirement-and-Survivor-Benefit-Exemption.pdf#page=2",
    )
    defined_for = StateCode.MT
