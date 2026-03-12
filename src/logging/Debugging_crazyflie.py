
import cflib 
import logging 
import time 

# importing libraries for cflib
import cflib.crtp    # for scanning Crazyflie instances 
from cflib.crazyflie import Crazyflie   # class used to connect/receive ans send data from Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie   # wrapper around Crazyflie to handle asynchronous nature of  Crazyflie API, 
                                                            # that is ensuring a connection is first setup before trying to communicate-send/receive with the Crazyflie instance 
from cflib.utils import uri_helper 

#------  importing libraries to read logging variables
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig    # a class representation of one log configuration that enables logging from the Crazyflie
from cflib.crazyflie.syncLogger import SyncLogger   # class provides synchronous access to log data from the Crazyflie.


uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

# Parameters function  that uses asynchronous implementation
def param_stab_est_callback (name, value):
    print('The crazyflie has parameter '+name+ ' set at number: '+ value)

def simple_param_async(scf, groupstr, namestr):
    """Function to get or set parameter values using group names and string, which make up the full string name. """

    cf = scf.cf
    full_name = groupstr + "." + namestr

    # Getting the value of a parameter
    # cf.param.add_update_callback(group= groupstr, name=namestr, cb=param_stab_est_callback)   

    # Setting the value of a parameter 
    # cf.param.set_value(full_name, 2)    # the default value = 2, so needs to be changed back to this
    time.sleep(1)

    cf.param.set_value(full_name, 1)
    time.sleep(1)


def log_stab_callback(timestamp, data, logconf):
    print('[%d][%s]: %s' % (timestamp, logconf.name, data))

def simple_log_async(scf, logconf):
    cf = scf.cf 
    cf.log.add_config(logconf)

    logconf.data_received_cb.add_callback(log_stab_callback)
    logconf.start()
    time.sleep(5)
    logconf.stop()

def simple_log(scf, logconf):
    with SyncLogger(scf, lg_stab) as logger:
        for log_entry in logger:
            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2] 

            print("[%d] [%s]: %s"%(timestamp, logconf_name, data))
            break

            # Getting accelerator logging info 
            # timestamp = log_entry[0]
            # data = log_entry[1]
            # logconf_name = log_entry[2] 
            # print("\nData in total is : ", data, '\n')
            # print("[%d] [%s]: Acc_x: %d | Acc_y: %d | Acc_z: %d"%(timestamp, logconf_name, data['acc.x'], data['acc.y'], data['acc.z']))
            # time.sleep(1.5)
            # break

def simple_connect():
    print("Yeah, I'm connected! : D")
    time.sleep(3)
    print("Now I will disconnect  :'(")


if __name__ == '__main__':
    # initialize the low-level drivers
    cflib.crtp.init_drivers()

    # Define the logging configuration 
    lg_stab = LogConfig(name="Stabilizer", period_in_ms=10)
    lg_stab.add_variable("stabilizer.roll", 'float')
    lg_stab.add_variable("stabilizer.pitch", 'float')
    lg_stab.add_variable("stabilizer.yaw", 'float')
    # lg_stab = LogConfig(name="acc", period_in_ms=10)
    # lg_stab.add_variable("acc.x", 'float')
    # lg_stab.add_variable("acc.y", 'float')
    # lg_stab.add_variable("acc.z", 'float')

    # add group parameter name
    group = "stabilizer"
    name = "estimator"

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # simple_connect()
        # simple_log(scf, lg_stab)
        # simple_log_async(scf, lg_stab)
        simple_param_async(scf, group, name)

