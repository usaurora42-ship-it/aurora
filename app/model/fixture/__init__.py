from app import logging
from app.model.country import ModelCountry
from app.model.language import ModelLanguage
from app.model.currency import ModelCurrency
import pycountry
import json

LOGGER = logging.getLogger(__name__)


class ModelFixtures():
    # Fixture Countries
    def countries(self):
        # check already imported
        if ModelCountry.query.count() > 0:
            return

        countries_imported = {}
        for c in list(pycountry.countries):
            if c.name.lower() in countries_imported:
                continue

            countries_imported[c.name.lower()] = 1
            country = ModelCountry()

            exists = ModelCountry.query.filter_by(
                name=c.name
            ).first()
            
            if exists is None:
                country.create_country({
                    'name': c.name,
                    'official_name': c.official_name if hasattr(c, 'official_name') else '',
                    'numeric_ref': int(c.numeric) if hasattr(c, 'numeric') else 0,
                    'alpha_2': c.alpha_2 if hasattr(c, 'alpha_2') else '',
                    'alpha_3': c.alpha_3 if hasattr(c, 'alpha_3') else ''
                })

    # Fixture Languages
    def languages(self):
        # check already imported
        if ModelLanguage.query.count() > 0:
            return

        language_imported = {}
        for l in list(pycountry.languages):
            if l.name.lower() in language_imported:
                continue

            language_imported[l.name.lower()] = 1
            language = ModelLanguage()

            exists = ModelLanguage.query.filter_by(
                name=l.name
            ).first()

            if exists is None:
                language.create_language({
                    'name': l.name,
                    'alpha_3': l.alpha_3 if hasattr(l, 'alpha_3') else ''
                })

    # Fixtures Currency
    def currencies(self):
        # check already imported
        if ModelLanguage.query.count() > 0:
            return

        currencies_improted = {}
        for c in list(pycountry.currencies):
            if c.name.lower() in currencies_improted:
                continue

            currencies_improted[c.name.lower()] = 1
            currency = ModelCurrency()

            exists = ModelCurrency.query.filter_by(
                name=c.name
            ).first()

            if exists is None:
                currency.create_currency({
                    'name': c.name,
                    'numeric_ref': int(c.numeric) if hasattr(c, 'numeric') else 0,
                    'alpha_3': c.alpha_3 if hasattr(c, 'alpha_3') else ''
                })

