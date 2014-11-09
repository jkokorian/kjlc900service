from numpy import log10,floor,ceil,sign
import re
from tinyrpc.dispatch import public

def _formatFloatValue(value):
    if value == 0:
        return 0
    
    expSign = sign(log10(value))
    if value > 1:
        expValue = floor(abs(log10(value)))
    else:
        expValue = ceil(abs(log10(value)))
    exponentString = "%+.0f" % int(expSign * expValue)
    
    valueString = ("%0.2e" % value)[:4]
    return valueString + "E" + exponentString

class KJLC925PiraniSensor(object):

    def __init__(self, serial, deviceAddress=253):
        """
        Creates a new instance of the KJLC900 Series Pirani sensor interface
        class.
        
        parameters
        ----------
        
        portIODevice: an instance of serial.Serial to communicate with the sensor over RS-232.
        """
        
        self.serial = serial
        self.deviceAddres = deviceAddress
    
    

    def _query(self,command,replyConverter=str):
        commandString = "@%i%s;FF" % (self.deviceAddres,command)
        self.serial.write(commandString)
        self.serial.flush()
        
        reply = self.serial.readall()
        try:
            if replyConverter is not None:
                value = replyConverter(re.findall(r"@253ACK(.*);FF",reply)[0])
                return value
        except:
            raise Exception("The device threw an error")
       
    @public
    def getDeviceType(self):
        """
        Returns the transducer device type.
        """
        
        value = self._query("DT?")
        return value
        
        
    @public   
    def getFirmwareVersion(self):
        """
        Returns the 925C firmware version.
        """
        
        value = self._query("FV?")
        return value
       
    @public
    def getHardwareVersion(self):
        """
        returns the 925C hardware version.
        """
        
        value = self._query("HV?")
        return value
   
    @public
    def getModelNumber(self):
        """
        returns the 925C model number.
        """
        
        value = self._query("MD?")
        return value
     
    @public  
    def getSerialNumber(self):
        """
        Returns the 925C serial number.
        """
        
        value = self._query("SN?")
        return value
       
    @public
    def getTimeOn(self):
        """
        Returns the number of hours the transducer has been on.
        """
        
        value = self._query("TIM?",int)
        return value
       
    @public
    def getTransducerTemperature(self,float):
        """
        Returns the 925C on-chip sensor temperature in degrees Celcius.
        """
        
        value = self._query("TEM?")
        return value
       
    @public
    def getPressure(self,float):
        """
        Returns the measured pressure from the 925.
        """
        pressure = self._query("PR1?")
        return pressure
       
    @public
    def getGasType(self):
        """
        Returns the gas type for measurement.
        """
        gasType = self._query("GT?").lower()
        return gasType
    
   
    @public
    def setGasType(self,gasType="air"):
        """
        Sets gas type for measurement. 
        The 925C measures thermal conductivity; using the gas calibration compensates for gas errors.
        
        Parameters
        ----------
        
        gasType: "air"|"argon"|"nitrogen"|"H2O"|"hydrogen"|"helium"
        """
        
        self._query("GT!%s" % gasType.upper())
        
    
       
    @public
    def calibrateAtmospheric(self,pressure):
        """
        Sets full scale readout for the 925C. 

        Vent the transducer to atmospheric pressure before performing atmospheric calibration.
        """

        self._query("ATM!%s" % _formatFloatValue(pressure))
       
    @public
    def calibrateVacuum(self):
        """
        Zeroes the 925C readout. 

        Evacuate the transducer to a pressure below 8x10-6 Torr before performing vacuum calibration.
        """
        self._query("VAC!")
       
    @public
    def setSetpoint(self,pressure):
        """
        Sets the set point value.

        The set point value is the pressure either below or above which the set point relay will
        be energized (i.e., N.O. and C contacts will be closed). 
        The direction of the set point (ABOVE or BELOW) is configured using the setSetpointDirection
        command. The set point must be enabled for the set point command to
        function
        """
        self._query("SP1!%s" % _formatFloatValue(pressure))
   
    @public
    def getSetpoint(self):
        """
        Reads the current set point value.
        """
        pressure = self._query("SP1?",float)
        return pressure

    def setHysteresisValue(self,pressure):
        """
        Sets the pressure value at which the set point relay will be de-energized (i.e., N.C. and O contacts will be
        closed). 

        The hysteresis value should be higher than the set point value if the
        set point direction is set to BELOW and lower than set point value if set point
        direction is set to ABOVE. If abnormal values are entered the command
        throw an exception and the current value will not be overwritten. The set
        point hysteresis values are always overwritten whenever a set point value is
        entered or the set point direction is changed.
        """

        self._query("SH1!%s" % _formatFloatValue(pressure))
   
    @public
    def getHysteresisValue(self):
        """
        Returns the pressure value at which teh set point relay will be de-energized.
        """

        pressure = self._query("SH1?",float)
        return pressure
   
    @public
    def setSetpointDirection(self,direction="BELOW"):
        """
        Sets the direction of the set point relay. 

        If the value is BELOW, then the relay will be energized below the set
        point value.

        parameters
        ----------

        direction: "ABOVE"|"BELOW"
        """

        self._query("SD1!%s", direction)
   
    @public
    def getSetpointDirection(self):
        """
        Returns the direction of the set point relay.
        """

        direction = self._query("SD1?")
        return direction
   
    @public
    def setSetpointEnabled(self,enabled=False):
        """
        Enables or disables the setpoint relay.
        """

        self._query("EN1!%s" ("ON" if enabled else "OFF"))
   
    @public
    def getSetpointEnabled(self):
        """
        Returns the setpoint relay enable status.
        """

        enabled = self._query("EN1?",str) == "ON"
        return enabled
   
    @public
    def getSetpointStatus(self):
        """
        Returns the status of the set point relay.
        """

        status = self._query("SS1?")
        return status