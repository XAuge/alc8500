CH01 = '\x00'
CH02 = '\x01'
CH03 = '\x02'
CH04 = '\x03'

DEL_CH_LOG     = '\x4c'  # Delete channel logging
GET_CH_FUN     = '\x61'  # Reading channel function
GET_CH_LOG     = '\x62'  # Getting log data at address
GET_DB_REC     = '\x64'  # Read database record (40 records)
GET_DEV_CFG    = '\x6A'  # Device Configuration
GET_LOG_IDX    = '\x69'  # Getting channel logging indexes
GET_LOG_BLK    = '\x76'  # Getting logging data block
GET_CH_MEASURE = '\x6D'  # Getting channel measurement
GET_CH_PARAM   = '\x70'  # Getting channel parameters
GET_TEMP       = '\x74'  # Getting temperatures
GET_FW         = '\x75'  # Getting Firmware and serial
GET_CFG_ADD0   = '\x65'  # Additional parameter 0
GET_CFG_ADD1   = '\x67'  # Additional parameter 1
GET_CFG_ADD2   = '\x68'  # Additional parameter 2
GET_CFG_ADD3   = '\x6a'  # Additional parameter 3
GET_CFG_ADD4   = '\x7a'  # Additional parameter 4                                                                                                                               

SET_CH_PARAM   = '\x50'  # Set channel parameter
SET_AKKU       = '\x44'  # Write database record
SET_CH_FUN     = '\x41'  # Set channel function
SET_CFG_ADD0   = '\x45'  # Additional parameter 0
SET_CFG_ADD1   = '\x47'  # Additional parameter 1
SET_CFG_ADD2   = '\x48'  # Additional parameter 2
SET_CFG_ADD3   = '\x4a'  # Additional parameter 3
SET_CFG_ADD4   = '\x5a'  # Additional parameter 4

PROG_CHARGE     = '\x01' # Laden
PROG_DIS        = '\x02' # Entladen
PROG_DIS_CHARGE = '\x03' # Entladen–Laden
PROG_TEST       = '\x04' # Test
PROG_SERVICE    = '\x05' # Wartung
PROG_FORM       = '\x06' # Formieren
PROG_CYCLE      = '\x07' # Zyklen
PROG_REFRESH    = '\x08' # Auffrischen

AKKU_TYPE  = [
  'NiCd','NiMH','Li-Ion 4.1','Li-Pol 4.2','Pb','LiFePo4','LiPo+ 4.35','NiZn','AGM/CA'
]

STATUS = {
  '00': "Idle",
  '2f': "Discharge",
  '50': "Charge",
  '0a': "Pause",
  '7a': "Trickle charge"
}

ALC_CFG1 = [ "Off", "On", "1min", "5min", "10min", "30min", "60min" ]
ALC_CFG2 = { 3: "ALBEEP_EN", 4: "BUBEEP_EN" }

