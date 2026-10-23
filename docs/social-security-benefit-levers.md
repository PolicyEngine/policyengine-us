# Social Security benefit levers

The benefit lever interface separates reported annual benefits from public
benefit outputs. The implementation plan is:

1. Preserve the four reported benefit components as pure inputs, with the
   existing effective uprating. Migrate legacy constructor inputs by period,
   retaining explicitly supplied final overrides.
2. Apply independent across-the-board and supplied payable-share factors, and
   one joint payment-year COLA factor with an initially inactive withholding
   term. Keep the default factors equal to one.
3. Audit stored scoring-data columns and the artifact identity before scoring.
4. Verify current-law equality, precedence, periods, branches, export/reload,
   factor properties, and a capped direct PE-US microsimulation.

The engine contract does not certify API or application field exposure.
Calculated benefit source modes are reserved for subsequent implementations.
No package-specific values are part of this interface.
