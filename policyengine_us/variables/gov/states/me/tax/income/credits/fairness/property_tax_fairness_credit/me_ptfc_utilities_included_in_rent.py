from policyengine_us.model_api import *


class me_ptfc_utilities_included_in_rent(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Amount of utilities included in rent for the Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME
    documentation = "A value of 0 means the utilities-in-rent amount is unknown, which triggers the 15%-of-gross-rent estimate on Schedule PTFC/STFC line 5c (applied in me_property_tax_fairness_credit_countable_rent). A known amount is entered as a positive dollar value."
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_pstfc_ff.pdf#page=2"
