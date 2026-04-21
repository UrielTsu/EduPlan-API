import pymysql
pymysql.install_as_MySQLdb()
pymysql.version_info = (2, 2, 1, "final", 0)
#Esta línea registra pymysql con ese alias
#  y evita errores de importación cuando se conecte a MySQL sin mysqlclient.