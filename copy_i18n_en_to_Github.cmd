for %%i in (
abeip
abpccc
advancedComponents
advancedScheduler
asciiFile
BACnet
controlcore
dashboardDesigner
dataFile
dataImport
dataPointDetailsView
deviceConfig
dnp3
egauge
envcands
excelReports
galil
graphicalViews
Haystack
http
internal
jmxds
jsonFileImport
log4jDS
log4JReset
loggingConsole
maintenanceEvents
mangoApi
mangoESConfiguration
MangoIOTools
mangoNoSqlDatabase
mangoUI
mbus
measurlogicDTSCell
meta
modbus
mqttClientDataSource
onewire
opcda
openv4j
pachube
pakbus
persistent
pid
pointLinks
pop3
reports
scheduledEvents
scripting
serial
snmp
sqlConsole
sqlds
ssh
sstGlobalScripts
sstGraphics
sstTheme
TCPIP
templateConfig
twilio
virtualDS
vmstat
watchlists
zwave
) do xcopy ..\..\Mango3.3\web\modules\%%i\classes\i18n.properties .\modules\%%i\classes\ /Y
xcopy ..\..\Mango3.3\classes\i18n.properties .\modules\lang_zh\classes\ /Y
pause