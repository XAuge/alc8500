#### Official ALC-8500 Application start

`java -jar ChargeProfessional-3.0.1.jar`

#### Python examples

`test_serial.py` - looking for USB devices

`get_usb_device.py` - looking for ALC8500 and reading some information

#### Usage of alc8500 library

```python
import alc8500
from time import sleep

# initialize USB serial interface and getting system information
alc = alc8500.alc8500(debug=True)

alc.dump_data(alc.data)
alc.dump_data(alc.accu)
```

##### Getting alc battery database

```python
import json
alc.read_db()
db = alc.get_data(alc.db)
print(json.dumps(db,sort_keys=True,indent=2))
```

##### Getting channel parameter/status

```python
for i in range(1,5):
  alc.get_ch_params(i)
alc.dump_data(alc.channel)

for i in range(1,5):
  data = alc.get_ch_status(i)
  print(json.dumps(data,sort_keys=True,indent=2))
```

##### Read actual channel values

```python
while True:
  data = alc.get_ch_values(1)
  print(data)
  sleep(5)
```

##### Start/Stop channel function

```python
alc.ch_stop(2)
alc.ch_start(2)
```

##### Getting log entries for channel

```python
# read all log entries for specified port
alc.get_ch_logs(1)
alc.dump_data(alc.log)

# get single log entry metadata
alc.get_ch_log(1,37704)

# get single logging data block
alc.get_block(1,2)

```

More functions will follow soon ;)
