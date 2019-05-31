import serial
import time
import logging
import os
from logging.handlers import RotatingFileHandler

# Enabling logging mechanism
log_dir = os.path.join(os.getcwd(), os.pardir, 'mfgtool_logs')
if not os.path.isdir(log_dir):
    try:
        os.mkdir(log_dir)
    except OSError as e:
        print 'Error occured when creating logs folder, Error = {}'.format(e)
handlers_log_file = os.path.join(log_dir, 'Handlers.log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler(handlers_log_file, maxBytes=25000000, backupCount=5)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# time to wait after sending a command. This number has been arrived at by
# trial and error
RANGE_DICT = {
    '300nJ': 2.95e-7,
    '30nJ': 2.95e-8,
    '3nJ': 2.95e-9,
    'read_bytes': 11
}

class EnergyMeterReadTimeOutException(Exception):
    def __init__(self):
        super(EnergyMeterReadTimeOutException, self).__init__('Read timed out')



class EnergyMeterCorruptionException(Exception):
    def __init__(self):
        super(EnergyMeterCorruptionException, self).__init__('Read timed out')


class EnergyMeterHandler(object):
    """
    Class to interface with Coherent's Energy meter.

    Energy meter accepts commands in the form of
    To set parameter: 'CONFigure:RANGe:SELect', <value>
    To read parameter: 'CONFigure:RANGe:SELect?', <read_bytes>

    Reply, if any, will be in the form
    3.0000e-9
    """
    _port = None

    def __init__(self, port, baud_rate=115200, timeout=0.5):
        """
        Creates serial port with parameters passed
        :param port: serial port for energy meter
        :param baud_rate: reading baud rate, should match the value set on the energy meter
        :param timeout: read timeout
        """
        assert port is not None
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.create_serial_port()
        self.retry_limit = 2

    def create_serial_port(self):
        """
        creates serial port with the parameters set in init
        :return:
        """
        self._port = serial.Serial(
            port=self.port,
            baudrate=self.baud_rate,
            timeout=self.timeout)

    def set_retry_limit(self, retry_limit):
        """
        We observed that sometimes we read 0 if the energy meter had not measured any value
        So we update retry_limit to make sure we are reading correct value
        :param retry_limit: integer value to set the retry limit
        :return:
        """
        self.retry_limit = retry_limit

    def get_retry_limit(self):
        """
        getter function for retry_limit
        :return: retry_limit
        """
        return self.retry_limit

    def set_timeout(self, time_out_value):
        """
        setter for time_out
        This closes the serial and re-opens the serial port
        :param time_out_value:
        :return:
        """
        self.close()
        self.timeout = time_out_value
        self.create_serial_port()

    def sendcmd(self, command, argument=None):
        """
        Send the specified command along with the argument, if any.
        :param command:
        :param argument:
        :return:
        """
        if self._port is None:
            return

        if argument is not None:
            tosend = str(command) + ' ' + str(argument)
        else:
            tosend = str(command)
        self._port.write(tosend)

    def get_energy_nj(self, recursion = 0):
        """
        Reads energy meter
        We need to retry more at low range (0-15nJ), whereas at high range data gets correct value in less retrys
        :param recursion: recursion is the number of retrys to make sure its a valid value
        :return:
        """
        self._port.flush()
        time.sleep(0.1)
        self.sendcmd('CONF:READ:CONT LAST\n')
        time.sleep(0.1)
        self.sendcmd('INIT\n')
        time.sleep(0.1)
        self.sendcmd('FETC:NEXT?\n')
        time.sleep(0.1)

        try:
            energy = self._readline(11)
        except:
            logger.debug('In readline exception')
            energy = 0

        try:
            energy = float(str(energy).strip())
            energy_nj = float(energy / 1e-09)
        except:
            recursion += 1
            if recursion < self.retry_limit:
                energy_nj = self.get_energy_nj(recursion)
            else:
                energy_nj = 0
            logger.debug('In float conversion exception')
        else:
            self.sendcmd('ABOR\n')
        return energy_nj

    def _readline(self, read_bytes=None):
        """
        Returns the number of bytes read from the serial.
        """
        if read_bytes is None:
            read_bytes = 1

        try:
            line = self._port.read(read_bytes)
        except:
            line = 0

        return line

    def _emit(self, *args):
        if len(args) == 1:
            prefix = ''
            message = args[0]
        else:
            prefix = ' ' + args[0]
            message = args[1]

    def set_value_energy_meter(self, set_command, value=None):
        """
        :param ser_port: energy meter serial port object
        :param set_command: command or property to set
        :param value: Value of the parameter to be set
        :return: None
        """

        if value is None:
            return

        try:
            self.sendcmd(str(set_command) + ' ' + str(value) + '\n')
        except Exception as e:
            logger.error('Error occured while writing to serial port Error = {0}'.format(e))

    def get_value_energy_meter(self, get_command, bytes_to_read=0):
        """
        Question mark is not necessary
        :param ser_port: energy meter serial port object
        :param get_command: command or property to read
        :param bytes_to_read: Number of bytes expected to be read
        :return:
        """

        if bytes_to_read is None:
            return

        read_value = None
        try:
            self.sendcmd(get_command + '\n')
        except Exception as e:
            logger.error('Error occured while writing to serial port Error = {0}'.format(e))

        try:
            read_value = self._readline(bytes_to_read)
        except Exception as e:
            logger.error('Error occured while reading from serial port Error = {0}'.format(e))

        return read_value


    def set_range(self, range):
        """
        Wrapper for set_value_energy_meter to specifically set energy meter range.
        :param range: Sets range to one of the dict values
        :return: None
        """
        if range is None:
            return
        if range not in RANGE_DICT.keys():
            return
        self.set_value_energy_meter('CONFigure:RANGe:SELect', RANGE_DICT[range])

    def get_range(self):
        """
        Wrapper for get_value_energy_meter to specifically get energy meter range
        :return: Current Energy Meter range
        """
        em_range = self.get_value_energy_meter('CONFigure:RANGe:SELect?', RANGE_DICT['read_bytes'])
        logger.debug('range = ' + str(em_range))
        if em_range == '0.000+e00' or not em_range:
            return 0
        else:
            return em_range

    def is_closed(self):
        if self._port:
            return False
        else:
            return True

    def close(self):
        if self._port:
            self._port.close()
            self._port = None

    def __del__(self):
        self.close()
