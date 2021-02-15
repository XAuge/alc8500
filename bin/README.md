#### Official ALC-8500 Application start

`java -jar ChargeProfessional-3.0.1.jar`

#### Python examples

`test_serial.py` - looking for USB devices

`get_usb_device.py` - looking for ALC8500 and reading some information

#### Usage of alc8500 library

```python
import alc8500

alc = alc8500.alc8500()
data = alc.dump_data(alc.data)

alc.read_db()
data = alc.dump_data(alc.db)
```

More functions will follow soon ;)
