# create migration
flask db stamp head
set FLASK_ENV=development flask db migrate

# aplicar alteração no banco
set FLASK_ENV=development flask db upgrade

# execure fixtures
FLASK_ENV=development flask fixtures

# executar projeto
FLASK_ENV=development flask run

# depois que criar uma nova tabela rodar o migration e o upgrade

# revisões pendentes
https://www.arundhaj.com/blog/multiple-head-revisions-present-error-flask-migrate.html