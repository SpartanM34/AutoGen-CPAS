import json
import logging
import sys

from jsonschema import ValidationError, validate

logging.basicConfig(level=logging.INFO, format="%(message)s")


# Load schema
def load_schema(schema_path):
    with open(schema_path, "r") as f:
        return json.load(f)

# Load instance JSON to validate
def load_instance(instance_path):
    with open(instance_path, "r") as f:
        return json.load(f)

# Perform validation
def validate_instance(instance_path, schema_path):
    schema = load_schema(schema_path)
    instance = load_instance(instance_path)
    try:
        validate(instance=instance, schema=schema)
        logging.info("✅ Validation passed for %s", instance_path)
    except ValidationError as ve:
        logging.error("❌ Validation failed for %s", instance_path)
        logging.error("Reason: %s", ve.message)
        logging.error("At: %s", list(ve.absolute_path))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logging.error("Usage: python validate_idp.py <instance.json> <schema.json>")
        sys.exit(1)

    instance_file = sys.argv[1]
    schema_file = sys.argv[2]
    validate_instance(instance_file, schema_file)
