from policyengine_us.model_api import *


class mi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan taxable income subtractions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/Schedule-1.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040.pdf",
        # MCL 206.30(1)(d), (e), (q): subtract amounts "to the extent included in adjusted gross income"
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-30",
        # 2025 MI-1040 booklet: who must file (page 3); Schedule 1 lines 11, 14, 16 (pages 14-15)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=3",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=14",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income
        # Dependents' income is not in federal AGI; they report it on their
        # own return, so person-level subtractions count only the head and
        # spouse.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
