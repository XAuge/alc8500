#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# ELV/Voltcraft ALC8500-2 battery charger serial communication library
#-------------------------------------------------------------------------------
import re
import sys
import json
import struct
import serial
import serial.tools.list_ports
from time import sleep
from binascii import hexlify
from constant import *

class data:
  pass

class alc8500:

  def __init__(self,debug=False):
    ''' looking for ALC8500 and initialize data structures '''
    self.dev = None
    self.debug = debug
    self.data = data()
    self.db = data()
    self.channel = data()
    self.accu = data()
    self.log = data()
    devs = serial.tools.list_ports.comports(include_links=False)
    for dev in devs:
      if re.search('ALC8500',dev.product):
        self.dev = dev.device
    try:
      self.alc = serial.Serial(
        self.dev, 38400, timeout=0,parity=serial.PARITY_EVEN, rtscts=0)
    except:
      print("ALC8500 not found!")
      sys.exit(1)
    self.sysinfo()
    self.get_config()
    self.temp()

  def dump_data(self,dump):
    ''' print object data as json '''
    print(json.dumps(vars(dump),sort_keys=True,indent=2))

  def get_data(self,dump):
    ''' return object data as json '''
    return vars(dump)

  def testBit(self,int_type, offset):
    ''' checking if bit set '''
    mask = 1 << offset
    return(int_type & mask)

  def in_conv(self,data):
    ''' convert/extract response data '''
    x = data.replace(b'\x05\x15',b'\05').\
      replace(b'\x05\x12',b'\02').replace(b'\x05\x13',b'\03')
    return x[1:len(x)-1]

  def out_conv(self,data):
    ''' convert request protocol data '''
    x = data.replace(b'\05',b'\x05\x15').\
      replace(b'\02',b'\x05\x12').replace(b'\03',b'\x05\x13')
    return b'\x02' +x+ b'\x03'

  def send(self,func,*args):
    ''' send requested data and return response '''
    req = struct.pack(">B",func)
    for i in args:
      if type(i) is int:
        if i > 255:
          req += struct.pack(">H",i)
        else:
          req += struct.pack(">B",i)
      elif type(i) is bytes:
        req += i
    request = self.out_conv(req)
    self.alc.write(request)
    response = b''
    i = 0
    while not i:
      sleep(0.2)
      i = self.alc.in_waiting  # bytes in buffer
      response += self.alc.read(i)
      if response[-1] != 3:    # waiting for final 0x03
        i = 0
    conv = self.in_conv(response)
    if self.debug:
      print("# Request: 0x" + " 0x".join(re.findall('..',request[1:-1].hex())))
      print("# Response: 0x" + " 0x".join(re.findall('..',conv.hex())))
    return conv

  def sysinfo(self):
    ''' u <0x68> <firmware version> <0xFF> <0xFF> <Serial> '''
    resp = self.send(GET_FW)
    if chr(resp[0]) == 'u': # Firmware
      self.data.hardware = {
        'fw_version': str(resp[2:10].decode("utf-8")).lstrip(),
        'serial': str(resp[12:22].decode("utf-8")),
        "usb_port": re.sub("[<>]"," ",str(self.alc))
      }

  def temp(self):
    ''' t <ext.sensor> <power-supply> <cooler> '''
    resp = self.send(GET_TEMP)
    if (chr(resp[0]) == 't' and len(resp) > 5): # Temperatur
      self.data.temperature = {
        'sensor': struct.unpack(">H", resp[1:3])[0] / 100,
        'power': struct.unpack(">H", resp[3:5])[0] / 100,
        'cooler': struct.unpack(">H", resp[5:7])[0] / 100
      }
    if resp[1] == 171:
      self.data.temperature['Sensor'] = 'n.c.'

  def read_db(self):
    ''' Getting stored battery database
    d <number> <name> <type> <cells> <capacity> <discharge current>
    <charge current> <delay C/D> <FLAGS> <fullFactor> <function> '''
    i = 0
    while i < 40:
      o = self.send(GET_DB_REC,i)
      if chr(o[0]) == 'd': # Dataset
        if o[11] != 255:
          data = {
            'name': str(o[2:11].decode("utf-8")),
            'accu_type': AKKU_TYPE[o[11]],
            'cells': int(o[12]),
            'capacity_mAh': struct.unpack('>i', o[13:17])[0] / 10000,
            'discharge_mA': int(struct.unpack(">H", o[17:19])[0] / 10),
            'charge_mA': int(struct.unpack(">H", o[19:21])[0] / 10),
            'delay_cd_60sec': int(struct.unpack(">H", o[21:23])[0] / 60),
            'flags': o[23],
            'charge_factor_percent': o[24],
            'func_release': o[25]
          }
          setattr(self.db,"{:02d}".format(i),data)
        i += 1

  def get_config(self):
    ''' Getting internal battery and configuration data '''
    o = self.send(GET_CFG_ADDR0)
    if chr(o[0]) == 'e':
      LiPol42 = {
        'delay': o[3],
        'final_discharge_voltage': struct.unpack('>H',o[1:3])[0]/1000,
        'loading_voltage': struct.unpack('>H',o[4:6])[0]/1000,
        'trickle_voltage': struct.unpack('>H',o[6:8])[0]/1000
      }
      NiZn = {
        'delay': o[10],
        'final_discharge_voltage': struct.unpack('>H',o[8:10])[0]/1000,
        'loading_voltage': struct.unpack('>H',o[11:13])[0]/1000,
        'trickle_voltage': struct.unpack('>H',o[13:15])[0]/1000
      }
      AGM_CA = {
        'delay': o[17],
        'final_discharge_voltage': struct.unpack('>H',o[15:17])[0]/1000,
        'loading_voltage': struct.unpack('>H',o[18:20])[0]/1000,
        'trickle_voltage': struct.unpack('>H',o[20:22])[0]/1000
      }

    o = self.send(GET_CFG_ADDR1)
    if chr(o[0]) == 'g':
      NiCd = {
        'delay': o[15],
        'final_discharge_voltage': struct.unpack('>H',o[1:3])[0]/1000,
        'cycle_count': o[11],
        'cycle_forming': o[13],
        'charge_cut_off': o[20]
      }
      NiMH = {
        'delay': o[16],
        'final_discharge_voltage': struct.unpack('>H',o[3:5])[0]/1000,
        'cycle_count': o[12],
        'cycle_forming': o[14],
        'charge_cut_off': o[21]
      }
      LiIon41 = {
        'final_discharge_voltage': struct.unpack('>H',o[5:7])[0]/1000,
        'delay': o[17]
      }
      LiPol42['final_discharge_voltage'] = struct.unpack('>H',o[7:9])[0]/1000
      LiPol42['delay'] = o[17]
      Pb = {
        'final_discharge_voltage': struct.unpack('>H',o[9:11])[0]/1000,
        'delay': o[18]
      }

    o = self.send(GET_CFG_ADDR2)
    if chr(o[0]) == 'h':
      LiIon41['loading_voltage'] = struct.unpack('>H',o[9:11])[0]/1000
      LiIon41['trickle_voltage'] = struct.unpack('>H',o[11:13])[0]/1000
      LiPol42['loading_voltage'] = struct.unpack('>H',o[13:15])[0]/1000
      LiPol42['trickle_voltage'] = struct.unpack('>H',o[15:17])[0]/1000
      Pb['loading_voltage'] = struct.unpack('>H',o[17:19])[0]/1000
      Pb['trickle_voltage'] = struct.unpack('>H',o[19:21])[0]/1000
      self.data.hardware['LowBatt_Cut_Voltage'] = struct.unpack('>H',o[21:23])[0]/1000

    o = self.send(GET_CFG_ADDR3)
    if chr(o[0]) == 'j':
      LiFePo4 = {
        'charge_cut_off': struct.unpack('>H',o[1:3])[0],
        'delay': o[3],
        'loading_voltage': struct.unpack('>H',o[4:6])[0]/1000
      }
      self.data.hardware['Display_Contrast'] = int(o[10])
      self.data.hardware['Config'] = ALC_CFG1[o[10] & 7]
      for k in ALC_CFG2.keys():
        if self.testBit(o[9],k):
          self.data.hardware['config'] = self.data.hardware['Config'] +","+ ALC_CFG2[k]

    o = self.send(GET_CFG_ADDR4)
    if chr(o[0]) == 'z':
      LiIon41['storage_voltage'] = struct.unpack('>H',o[1:3])[0]/1000
      LiPol42['storage_voltage'] = struct.unpack('>H',o[3:5])[0]/1000
      LiFePo4['storage_voltage'] = struct.unpack('>H',o[5:7])[0]/1000
      NiZn['storage_voltage'] = struct.unpack('>H',o[7:9])[0]/1000

    self.accu.LiPol42 = LiPol42
    self.accu.LiIon41 = LiIon41
    self.accu.LiFePo4 = LiFePo4
    self.accu.AGM_CA = AGM_CA
    self.accu.NiZn = NiZn
    self.accu.NiMH = NiMH
    self.accu.NiCd = NiCd
    self.accu.Pb = Pb

  def _isport(self,port):
    if port in [ 1,2,3,4 ]:
      return True
    else:
      print("Channel/port number should be between 1 and 4!")
      return False

  def _get_status(self,status):
    for key in STATUS.keys():
      if (status >= STATUS[key][0] and status <= STATUS[key][1]):
        return key
    return "unknown"

  def get_ch_params(self,port):
    ''' Getting stored channel parameters
    p <ch-number> <batt-number> <batt-type> <cells> <discharge current>
    <charge current> <capacity> <prog-number> <forming current>
    <delay C/D> <FLAGS> <measure end> <full factor> '''
    if self._isport(port):
      o = self.send(GET_CH_PARAM,port-1)
      if chr(o[0]) == 'p': # Channel parameter
        data = {
          'accu_number': o[2],
          'accu_type': AKKU_TYPE[o[3]],
          'cells': int(o[4]),
          'discharge_mA': int(round(struct.unpack(">H", o[5:7])[0]/10)),
          'charge_mA': int(round(struct.unpack(">H", o[7:9])[0]/10)),
          'capacity_mAh': int(round(struct.unpack('>i', o[9:13])[0] / 10000)),  # struct.pack('>i',cap)
          'function': CH_FUNCTION[int(o[13])],
          'form_charge_mA': int(round(struct.unpack(">H", o[14:16])[0] / 60)),  # struct.pack(">H",mA)
          'delay_cd_60sec': struct.unpack(">H", o[16:18])[0] / 60,
          'flags': o[19],
          'measure_end': struct.unpack(">H", o[19:21])[0],
          'charge_factor_percent': o[21]
        }
        setattr(self.channel,str(port),data)

  def get_ch_values(self,port):
    ''' Getting last channel measurement values
    m <port number> <voltage> <current> <capacity> '''
    if self._isport(port):
      o = self.send(GET_CH_MEASURE,port-1)
      if chr(o[0]) == 'm': # Measurement
        data = {
          'port': port,
          'voltage': struct.unpack(">H", o[2:4])[0] / 1000,
          'milliampere': struct.unpack(">H", o[4:6])[0]/10,
          'capacity': struct.unpack('>i', o[6:10])[0] / 10000
        }
        return data

  def get_ch_status(self,port):
    ''' a <portnumber>  -> function (1 byte) '''
    if self._isport(port):
      o = self.send(GET_CH_FUN,port-1)
      if chr(o[0]) == 'a':
        data = {
          'port': port,
          'function': self._get_status(o[2])
        }
        return data

  def get_block(self,port,block):
    ''' Getting logging block, block = 0..650 '''
    if self._isport(port):
      o = self.send(GET_LOG_BLK,port-1,struct.pack(">H",block))

  def get_ch_log(self,port,addr):
    ''' Getting battery and function data from log entry '''
    if self._isport(port):
      o = self.send(GET_CH_LOG,port-1,addr)

  def get_ch_logs(self,port):
    ''' getting log addresses/blocks for selected port
    i <portnumber>  '''
    if self._isport(port):
      o = self.send(GET_LOG_IDX,port-1)
      print(o)
      if chr(o[0]) == 'i':
        addrs = [ int(i,16) for i in re.findall('....',str(hexlify(o[2:]),'ascii')) ]
        addrs[:] = (i for i in addrs if i != 65535) # remove unused
        last = addrs[0]
        if len(addrs) == 12:
          idx = addrs[1:].index(last) +3
          if idx < 8:
            addrs[:] = addrs[idx:] + addrs[1:idx]
            self.log.addrs = { 'addrs': addrs }
            for i in range(len(addrs)-1):
              size = addrs[i+1] - addrs[i]
              blk = divmod(size,100)
              data = {
                  'size': size,
                  'addr': addrs[i],
                  'blks': blk[0],
                  'leftover': blk[1]
              }
              setattr(self.log,str(i),data)
              print(addrs[i],size)
          # if idx = 9 move <end> to end of list and delete index 00
        else:
          pass
        print(addrs)

  def ch_stop(self,port):
    if self._isport(port):
      o = self.send(SET_CH_FUN,port-1,1)
      return self.get_ch_status(port)

  def ch_start(self,port):
    if self._isport(port):
      o = self.send(SET_CH_FUN,port-1,0)
      return self.get_ch_status(port)
