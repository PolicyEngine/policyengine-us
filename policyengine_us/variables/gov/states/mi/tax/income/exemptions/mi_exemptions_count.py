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
        "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf",
        "https://www.michigan.gov/treasury/-/media/Project/Websites/treasury/Uncategorized/2023/Economic-Reports-and-Notices-2023/Home-Heating-Expenses-Reported-by-Home-Heating-Credit-Filers/rpt-text_2021data.pdf#page=2",
        "https://web.archive.org/web/20220523104347/https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/IIT/BOOK_MI-1040CR-7.pdf?rev=d7990c15e0034d768a43c47b6d3ba0ac#page=7",
    )
    adds = [
        "tax_unit_size",
        "mi_disabled_exemption_eligible_person",
        "is_fully_disabled_service_connected_veteran",
    ]
