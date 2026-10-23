from policyengine_us.model_api import *


class mt_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Montana LIHEAP household size"
    defined_for = StateCode.MT
    reference = (
        "https://rules.mt.gov/policy-library-documents/application/pdf/5475239b875d29ebe7cf1f12b38458830f87a4a18c8dd600b7548603204fccd9#page=2",
        "https://rules.mt.gov/policy-library-documents/application/pdf/5389d31b170322ad8de7c67ca74832a2fe762425962ec410fe9a737193afe951#page=1",
        # PDF pages 1-2
        "https://rules.mt.gov/policy-library-documents/application/pdf/325b36e5abb6a3bfa036c3802fc997ed50711b5407868ec8f4b61eabc538e3ed#page=1",
        # PDF pages 1-2
        "https://rules.mt.gov/policy-library-documents/application/pdf/fa158b2cdbf766e585e1fbf5811523e0dff4e760111590ae75d0456ee81551ad#page=1",
        # PDF pages 36, 58
        "https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=36",
    )

    # ARM 37.70.402(8) (numbered (7) from May 23, 2026): only citizens and
    # qualified aliens count toward size, while ineligible members' income
    # counts in full. SPM membership approximates the economic unit;
    # foster-member elections, custody splits and temporary absences are not
    # modeled.
    adds = ["is_citizen_or_legal_immigrant"]
