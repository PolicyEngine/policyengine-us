"""IRS uprating parameter setup.

This module imports the unified uprating extension functionality.
The actual extension logic is in parameters/uprating_extensions.py.
"""

from policyengine_us.parameters.uprating_extensions import (
    set_all_uprating_parameters as set_irs_uprating_parameter,
)

# For backward compatibility, we keep the same function name
# but it now calls the unified function that handles all uprating parameters
