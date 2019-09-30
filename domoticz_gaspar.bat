
#Change below to your parameters
set GASPAR_USERNAME=mon@email.com
set GASPAR_PASSWORD=mon_pass
set DOMOTICZ_ID=id_of_domoticz_device

#do not change below
set BASE_DIR=%cd%
set CFG_FILE=domoticz_gaspar.cfg
set LOG_FILE=domoticz_gaspar.log
set PY_SCRIPT=gaspar_json.py
set PY_SCRIPT=%BASE_DIR%\%PY_SCRIPT%



python %PY_SCRIPT% %1 -o %BASE_DIR% >> %BASE_DIR%\%LOG_FILE% 
  if errorlevel 0 (
    node %BASE_DIR%\domoticz_gaspar.js %DOMOTICZ_ID% > %BASE_DIR%\req.sql
    cat %BASE_DIR%\req.sql | sqlite3 \domoticz\domoticz.db
)