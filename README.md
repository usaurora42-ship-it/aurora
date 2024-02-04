# create migration
FLASK_ENV=development flask db migrate

# aplicar alteração no banco
FLASK_ENV=development flask db upgrade

# execure fixtures
FLASK_ENV=development flask db fixtures

# executar projeto
FLASK_ENV=development flask run