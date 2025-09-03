# phone_lookup.py
import re
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from phonenumbers.phonenumberutil import NumberParseException

TYPE_MAP = {
    phonenumbers.PhoneNumberType.MOBILE: "MOBILE",
    phonenumbers.PhoneNumberType.FIXED_LINE: "FIXED_LINE",
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "FIXED_LINE_OR_MOBILE",
    phonenumbers.PhoneNumberType.TOLL_FREE: "TOLL_FREE",
    phonenumbers.PhoneNumberType.PREMIUM_RATE: "PREMIUM_RATE",
    phonenumbers.PhoneNumberType.SHARED_COST: "SHARED_COST",
    phonenumbers.PhoneNumberType.VOIP: "VOIP",
    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "PERSONAL_NUMBER",
    phonenumbers.PhoneNumberType.PAGER: "PAGER",
    phonenumbers.PhoneNumberType.UAN: "UAN",
    phonenumbers.PhoneNumberType.VOICEMAIL: "VOICEMAIL",
    phonenumbers.PhoneNumberType.UNKNOWN: "UNKNOWN",
}


def normalize_number(number: str) -> str:
    """Remove spaces, dashes, and brackets but keep leading + if present."""
    return re.sub(r"[^\d+]", "", number)


def lookup_phone(number: str, region: str = None) -> dict:
    """Lookup details about a phone number using the phonenumbers library."""
    try:
        number = normalize_number(number)
        parsed = phonenumbers.parse(number, region)

        # Validity checks
        valid = phonenumbers.is_valid_number(parsed)
        possible = phonenumbers.is_possible_number(parsed)

        # Type
        num_type = phonenumbers.number_type(parsed)
        type_str = TYPE_MAP.get(num_type, "UNKNOWN")

        # Carrier / Region / Timezone
        carrier_name = carrier.name_for_number(parsed, "en") or "N/A"
        region_name = geocoder.description_for_number(parsed, "en") or "N/A"
        tz = timezone.time_zones_for_number(parsed) or ["N/A"]

        # Formats
        formats = {
            "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            "international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
        }

        return {
            "number": formats["e164"],
            "valid": valid,
            "possible": possible,
            "region": region_name,
            "carrier": carrier_name,
            "type": type_str,
            "timezones": list(tz),
            "formats": formats,
        }

    except NumberParseException as e:
        return {"error": f"Invalid number: {e}"}
    except Exception as e:
        return {"error": str(e)}
