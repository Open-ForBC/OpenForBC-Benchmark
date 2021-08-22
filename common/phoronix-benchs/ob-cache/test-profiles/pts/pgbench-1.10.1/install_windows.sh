#!/bin/sh

unzip -o postgresql-13.0-1-windows-x64-binaries.zip
rm -rf $HOME/pg_
mkdir -p $HOME/pg_/data/postgresql/extension/
touch $HOME/pg_/data/postgresql/extension/plpgsql.control

# initialize database with encoding and locale
cd pgsql/bin
./initdb.exe -D $HOME/db --encoding=SQL_ASCII --locale=C
cd ~

echo "If this test fails to run, you may need to manually install the Microsoft Visual C++ Redistributable package for MSVCR120.dll: https://www.microsoft.com/en-us/download/details.aspx?id=40784" > ~/install-message

echo "#!/bin/sh
PGDATA=\$HOME/db/
PGPORT=7777
export PGDATA
mkdir db
export PGPORT
# start server
./pgsql/bin/pg_ctl.exe start -o '-c autovacuum=false -c max_connections=300'
# wait for server to start
sleep 10

# create test db
./pgsql/bin/createdb.exe pgbench

./pgsql/bin/pgbench.exe -i \$1 \$2 -n pgbench

# run the test 
./pgsql/bin/pgbench.exe -j \$NUM_CPU_CORES \$@ -n -T 15 -r pgbench >\$LOG_FILE
# drop test db
./pgsql/bin/dropdb.exe pgbench
# stop server
./pgsql/bin/pg_ctl.exe stop" > pgbench
chmod +x pgbench

