from policyengine_us.model_api import *


class mi_military_and_railroad_retirement_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Michigan military and railroad retirement subtraction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Schedule 1 line 11: retirement benefits for service in the Armed "
        "Forces or the Michigan National Guard and the Railroad Retirement Act "
        "benefits in federal adjusted gross income, which MCL 206.30(1)(e) "
        "deducts. The retirement and pension benefits subtraction "
        "(subsection (1)(f)(iv)), the senior interest, dividends and capital "
        "gains deduction (subsection (1)(p)) and the Michigan standard "
        "deduction (subsection (9)) count this amount against their limits."
    )
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-30",
        # 2025 MI-1040 book: the dividend, interest and capital gains
        # worksheet, line 2 (page 17); Worksheet 2, line 5 (page 18); Form
        # 4884 line 10 (page 21); Worksheets 3.1 and 3.2, line 2 (page 24);
        # Worksheet 3.3, line 2 (page 25).
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=17",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=18",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=21",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=24",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=25",
    )
    defined_for = StateCode.MI
    adds = ["mi_military_retirement_subtraction", "taxable_railroad_benefits"]
