# backend
backend para front de proyectos

## Base de datos en desarrollo

El backend usa Django 5.

Por defecto el proyecto sigue usando SQLite en local para que puedas desarrollar sin depender de la base MySQL. Si quieres usar MariaDB o MySQL con `my.cnf`, recuerda que Django 5 exige MariaDB 10.6 o superior.

- Ejecutar migraciones: `python manage.py migrate`
- Levantar servidor: `python manage.py runserver`

Si quieres forzar MySQL o MariaDB con `my.cnf`, usa:

- PowerShell: `$env:EDUPLAN_DB_ENGINE = 'mysql'`
- Luego: `python manage.py migrate`

Opcionalmente puedes cambiar la ruta del archivo SQLite con `EDUPLAN_SQLITE_NAME`.
