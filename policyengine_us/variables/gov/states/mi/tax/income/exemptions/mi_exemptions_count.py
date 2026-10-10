from policyengine_us.model_api import *


class mi_exemptions_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan exemptions count"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-30",
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-527a",
        "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf",
        "https://www.michigan.gov/treasury/-/media/Project/Websites/treasury/Uncategorized/2023/Economic-Reports-and-Notices-2023/Home-Heating-Expenses-Reported-by-Home-Heating-Credit-Filers/rpt-text_2021data.pdf#page=2",
        "https://web.archive.org/web/20220523104347/https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/IIT/BOOK_MI-1040CR-7.pdf?rev=d7990c15e0034d768a43c47b6d3ba0ac#page=7",
        "https://taxsim.nber.org/historical_state_tax_forms/MI/2025/MI-1040CR-7%20Book.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        # MCL 206.527a(1)(c)(i) bases the home heating standard allowance on
        # the exemptions claimed on the income tax return, plus dependency
        # exemptions for household members under a custodial arrangement
        # "even if the exemptions may not be claimed for other income tax
        # purposes". The MI-1040CR-7 instructions allow an exemption for
        # "Yourself, unless you are eligible to be claimed as a dependent on
        # someone else's return", and for children who live with you "even if
        # their support comes from ... someone else". So a filer whom another
        # taxpayer can claim adds no exemption; on a joint claim the other
        # spouse, the children and the special exemptions still count.
        size = tax_unit("tax_unit_size", period)
        filers = add(tax_unit, period, ["is_tax_unit_head_or_spouse"])
        independent_filers = tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        special = add(
            tax_unit,
            period,
            [
                "mi_disabled_exemption_eligible_person",
                "is_fully_disabled_service_connected_veteran",
            ],
        )
        return size - (filers - independent_filers) + special
