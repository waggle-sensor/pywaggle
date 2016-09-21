
# from http://code.activestate.com/recipes/577911-context-manager-for-a-daemon-pid-file/

# Dual licensed under the MIT and GPL licenses.

import fcntl
import os
import os.path
import subprocess
import time
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


def read_file( str ):
    print(("read_file: "+str))
    if not os.path.isfile(str) :
        return ""
    with open(str,'r') as file_:
        return file_.read().strip()
    return ""
    

class PidFile(object):
    """Context manager that locks a pid file.  Implemented as class
    not generator because daemon.py is calling .__exit__() with no parameters
    instead of the None, None, None specified by PEP-343."""
    # pylint: disable=R0903

    def __init__(self, path, force=0, name=''):
        self.path = path
        self.pidfile = None
        self.force = force
        self.name = name


    def get_process_group(self, pid):
        
        gpid_str = None
        ps_command = ['ps', '-o','pgid', '--no-headers', str(pid)]
        logger.debug(' '.join(ps_command))
        try:
            gpid_str = subprocess.Popen(ps_command, stdout=subprocess.PIPE).communicate()[0]
        except Exception as e:
            logger.warning("Could not get process group id: (%s) %s" % (str(type(e)),str(e)) )
            return None
        
        if not gpid_str:
            logger.warning("GPID for PID %s not found" % (str(pid)))
            return None
        
            
        try:
            gpid_int = int(gpid_str)
        except Exception as e:
            logger.warning("Could not convert process group id: (%s) %s" % (str(type(e)),str(e)) )
            return None
          
        if gpid_int <= 1:
            logger.warning("gpid_int <= 1 : %d" % (gpid_int))
            return None
        
        return gpid_int
        

    def kill_process_group(self, pgid):
        
        kill_command = ['kill','-TERM', '-'+str(pgid)]
        logger.debug(' '.join(kill_command))
        try:
            subprocess.call(kill_command, shell=False)
        except Exception as e:
            logger.warning("Kill failed: (%s) %s" % (str(type(e)),str(e)) )
            return 0
            
        return 1
    

    def __enter__(self):
        
        # this is not a real loop, I just want to be able to break out
        while self.force:
            """
            This will try to kill an existing process group.
            """
            other_pid = read_file(self.path)
            
            # get process group id
            
            if not other_pid:
                break;
            
            pgid_int = self.get_process_group(other_pid)
            if not pgid_int:
                break
            
            
            if not self.kill_process_group(pgid_int):
                break
            
            
            time.sleep(3)
            try:
                os.remove(self.pidfile)
            except:
                pass
            
            break  
                
        directory = os.path.dirname(self.path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        self.pidfile = open(self.path, "a+")
        try:
            fcntl.flock(self.pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
                raise AlreadyRunning("Already running according to " + self.path)
                
                
        self.pidfile.seek(0)
        self.pidfile.truncate()
        self.pidfile.write(str(os.getpid()))
        self.pidfile.flush()
        self.pidfile.seek(0)
        return self.pidfile

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        try:
            self.pidfile.close()
        except IOError as err:
            # ok if file was just closed elsewhere
            if err.errno != 9:
                raise
        os.remove(self.path)


class AlreadyRunning(Exception):
    pass

# example usage
#import daemon
#context = daemon.DaemonContext()
#context.pidfile = PidFile("/var/run/mydaemon")