# encoding: utf-8
import cerberus
import re
import json
import logging
import pycountry
from decimal import Decimal
from datetime import datetime, time
from pytz import timezone
from ipaddress import ip_address, ip_network
from sqlalchemy import text
from email_validator import validate_email, EmailNotValidError

from app import db

LOGGER = logging.getLogger(__name__)

# decimal type
decimal_type = cerberus.TypeDefinition('decimal', (Decimal,), ())

class ModelValidator(cerberus.Validator):
    types_mapping = cerberus.Validator.types_mapping.copy()
    types_mapping['decimal'] = decimal_type

    # Custom Validators
    def _check_with_occupation_id(self, field, value):
        try:
            engine = db.get_engine()
            with engine.connect() as con:
                rs = con.execute(text('SELECT id FROM cbos WHERE code = :v'),  v=value)
                cbo = 0
                for row in rs:
                    cbo += 1

                if cbo == 0:
                    self._error(field, 'must be occupation_id valid, please check list CBOs')
                    return False

            return True
        except Exception as e:
            LOGGER.exception(e)
            self._error(field, 'internal error validation occupation_id')
            return False

    def _check_with_ip_address(self, field, value):
        if value is None or value == '':
            return True

        for addr in [a.strip() for a in value.split(',')]:
            
            try:
                version = ip_address(addr).version
            except Exception as e:
                try:
                    version = ip_network(addr).version
                except Exception as e:
                    self._error(field, '%s is not a valid ip address' % addr)
                    return False
        return True

    def _check_with_email(self, field, value):
        try:
            valid = validate_email(value, allow_smtputf8=False)
        except EmailNotValidError as e:
            self._error(field, 'must be a valid email addreess')
            return False
        return True

    def _check_with_language(self, field, value):
        try:
            language = pycountry.languages.lookup(value)
        except Exception as e:
            self._error(field, 'must be a language option')
            return False
        return True

    def _check_with_str_as_number(self, field, value):
        try:
            if type(value) == int or re.match(r'^\d+$', str(value)) is None:
                self._error(field, 'invalid string as a number')
                return False
            return True
        except Exception as e:
            self._error(field, 'invalid string as a number')
            return False

    def _check_with_country(self, field, value):
        try:
            country = pycountry.countries.lookup(value)
        except Exception as e:
            self._error(field, 'must be a country option')
            return False
        return True

    def _check_with_currency(self, field, value):
        try:
            currency = pycountry.currencies.lookup(value)
        except Exception as e:
            self._error(field, 'must be a currency option')
            return False
        return True

    def _check_with_json(self, field, value):
        try:
            data = json.dumps(value)
        except Exception as e:
            self._error(field, 'must be a json data')
            return False
        return True

    def _check_with_json_array_currencies(self, field, value):
        try:
            data = json.dumps(value)
            if type(value) != list:
                self._error(field, 'must be a array data')
                return False

            for curr in value:
                try:
                    currency = pycountry.currencies.lookup(curr)
                except Exception as e:
                    self._error(field, '%s is not a valid currency' % curr)
                    return False

        except Exception as e:
            self._error(field, 'must be a json data')
            return False
        return True

    def _check_with_timezone(self, field, value):
        try:
            tz = timezone(value)
            return True
        except Exception as e:
            self._error(field, 'must be timezone data')
            return False

        return True

    def _check_with_time(self, field, value):
        try:
            data = [ int(v) for v in value.split(':') ]

            if len(data) == 1:
                t = time(data[0])
            elif len(data) == 2:
                t = time(data[0], data[1])
            elif len(data) == 3:
                t = time(data[0], data[1], data[2])
            else:
                raise 'invalid data'
            return True
        except Exception as e:
            self._error(field, 'must be time data format')
            return False

        return True

    def _check_with_password(self, field, value):
        try:
            if re.match(r'^(?=.*\d)(?=.*[$&+=\?@#\|\'\<\>\.\^\*\(\)%\!\-])[A-Za-z\d$&\+\=\?@#\|\'\<\>\.\^\*\(\)%\!\-]{6,}$', value) is None:
                self._error(field, 'invalid password')
                return False
            return True
        except Exception as e:
            self._error(field, 'invalid password')
            return False

        return True

    # Custom Coerces
    def _normalize_coerce_datetime(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            pass

    # Custom Coerces
    def _normalize_coerce_document_number(self, value):
        try:
            if value:
                value = re.sub(r'\D', '', value)
            return value
        except Exception as e:
            pass

    def _normalize_coerce_date(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except Exception as e:
            pass

    def _normalize_coerce_date_maybe_time(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            try:
                return datetime.strptime(value, '%Y-%m-%d')
            except Exception as e:
                pass

    def _normalize_coerce_money(self, value):
        try:
            return float(format(float(value), '.2f'))
        except Exception as e:
            pass

    def _normalize_coerce_boolean(self, value):
        if value in [False, 'false', 0]:
            return 'false'
        elif value in [True, 'true', 1]:
            return 'true'
        else:
            return value

    def _normalize_coerce_integer(self, value):
        try:
            return int(value)
        except Exception as e:
            pass

    def _normalize_coerce_float(self, value):
        try:
            return float(value)
        except Exception as e:
            pass

    def _normalize_coerce_float_none(self, value):
        try:
            if value:
                return float(value)
            else:
                return None
        except Exception as e:
            pass

    def _normalize_coerce_str(self, value):
        try:
            return str(value)
        except Exception as e:
            pass