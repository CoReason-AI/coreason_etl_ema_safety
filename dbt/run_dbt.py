import sys
from typing import Any

# --- MONKEY PATCH FOR PYTHON 3.14 COMPATIBILITY ---
# Pydantic v1 (used by dbt) completely breaks on Python 3.14 due to changes in type annotations.
# We aggressively patch its internal type-checker to bypass these crashes.
import pydantic.v1.config
import pydantic.v1.fields
import pydantic.v1.errors

# 1. Allow arbitrary types globally
pydantic.v1.config.BaseConfig.arbitrary_types_allowed = True

# 2. Catch the exact ConfigError and force the type to 'Any'
original_set_default = pydantic.v1.fields.ModelField._set_default_and_type

def patched_set_default(self):
    try:
        original_set_default(self)
    except pydantic.v1.errors.ConfigError as e:
        if "default_factory" in str(e):
            self.type_ = Any
            self.outer_type_ = Any
            self.required = False
        else:
            raise

pydantic.v1.fields.ModelField._set_default_and_type = patched_set_default
# --------------------------------------------------

from dbt.cli.main import cli

if __name__ == '__main__':
    sys.exit(cli())
