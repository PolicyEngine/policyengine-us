from policyengine_us.model_api import *


class mt_military_retirement_exemption_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the residency and timing conditions of the Montana military retirement exemption"
    definition_period = YEAR
    default_value = True
    documentation = (
        "MCA 15-30-2120(9): the retiree or survivor became a Montana resident "
        "after June 30, 2023 (on or after that date for tax years from 2026, "
        "under 2025 Mont. Laws ch. 586), or was a Montana resident before the "
        "military retirement pay or survivor benefits began and has remained "
        "one; claims the exemption within five consecutive years of meeting "
        "that condition (tax years 2024 through 2028 for a resident from "
        "before July 2023, by the Form WMRE instructions); and has not "
        "claimed it and then moved out of Montana. Set this to false for a "
        "filer who fails any of these conditions. PolicyEngine has no other "
        "input for these facts, so the default of true overstates the "
        "exemption in two known ways. From 2024, it includes a resident from "
        "before July 2023 whose "
        "pay or benefits began while living in another state. From 2029, it "
        "also includes every filer whose five years have run out, starting "
        "with those whose five years began in 2024. As a benchmark for "
        "microsimulation totals, the Montana Revenue Interim Committee's "
        "November 2025 memo reports 1,711 resident claimants and $24.8 "
        "million for tax year 2024 (more than 1,783 claimants and $25.5 "
        "million with nonresidents and part-year residents)."
    )
    reference = (
        "https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://archive.legmt.gov/bills/2023/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://archive.legmt.gov/content/Sessions/69th/Contractor_index/CH0586.pdf#page=6",
        "https://revenue.mt.gov/files/Forms/Montana-Working-Military-Retirement-and-Survivor-Benefit-Exemption.pdf#page=2",
        "https://archive.legmt.gov/content/Committees/Interim/2025-2026/RIC/Meetings/November_12_13_2025/veteran-tax-benefits.pdf#page=1",
    )
    defined_for = StateCode.MT
