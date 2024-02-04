# encoding: utf-8
import base64
import hashlib
import uuid
import string
import random
import pycountry
from decimal import Decimal
from enum import Enum
from datetime import time, date, datetime
from ipaddress import ip_address, ip_network
import logging
import re

LOGGER = logging.getLogger(__name__)


class IPAddress():
    error = None
    def ip_address_in(self, ip, list_ip):
        self.error = None

        ip_is_valid = False
        client_addr = None
    
        try:
            client_addr = ip_address(ip)

        except Exception as e:
            self.error = {'errors': {'ip_address': ['the ip_address %s is not valid' % ip]}}
            return False

        for addr in [a.strip() for a in list_ip.split(',')]:
            try:
                check_addr = ip_address(addr)
                if check_addr == client_addr:
                    ip_is_valid = True
                    break

            except Exception as e:
                try:
                    check_addr = ip_network(addr)
                    if client_addr in check_addr:
                        ip_is_valid = True
                    break

                except Exception as e:
                    pass

        return ip_is_valid

class Util():
    def md5_hex(self, value):
        if value is None or not isinstance(value, str):
            return

        return hashlib.md5(value.encode('utf-8')).hexdigest()

    def encrypt_password(self, password):
        return base64.b64encode(hashlib.sha1(str(password).encode('utf-8')).digest()).decode()

    def gen_uuid(self, value=None):
        if value is None:
            return str(uuid.uuid4())
        else:
            md5_data = hashlib.md5(value.encode('utf-8')).hexdigest()
            return re.sub(r'([a-f0-9]{8})([a-f0-9]{4})([a-f0-9]{4})([a-f0-9]{4})([a-f0-9]{12})', '\\1-\\2-\\3-\\4-\\5', md5_data)

    def gen_apikey(self, size=27):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

    def gen_sms_code(self, size=6):
        return ''.join(random.choices(string.digits, k=size))

    def language_lookup(self, value):
        try:
            language = pycountry.languages.lookup(value)
            return language.name
        except Exception as e:
            LOGGER.exception(e)
            return None

    def country_lookup(self, value):
        try:
            country = pycountry.countries.lookup(value)
            return country.name
        except Exception as e:
            LOGGER.exception(e)
            return None

    def currency_lookup(self, value):
        try:
            currency = pycountry.currencies.lookup(value)
            return currency.name
        except Exception as e:
            LOGGER.exception(e)
            return None

    def get_dict(self, obj, keys):
        data = {}
        for k in sorted(keys):
            value = getattr(obj, k, None)

            # str and int
            if value is None or isinstance(value, int) or isinstance(value, float) or isinstance(value, str):
                pass

            # Enum
            elif isinstance(value, Enum):
                value = value.name
                if value == 'true' or value == 'false':
                    value = value == 'true'

            # decimal
            elif isinstance(value, Decimal):
                value = float(value)

            # date time
            elif isinstance(value, time) or isinstance(value, date) or isinstance(value, datetime):
                value = str(value)

            data[k] = value
        return data

    def format_cpf(self, cpf):
        try:
            cpf = re.sub(r'\D', '', cpf)
            cpf = re.sub(r'(\d{3})(\d{3})(\d{3})(\d{2})', '\\1.\\2.\\3-\\4', cpf)
        except Exception as e:
            LOGGER.exception(e)
        
        return cpf
