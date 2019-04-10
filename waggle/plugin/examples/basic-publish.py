# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
import waggle.plugin
import time

# Initialize our test plugin.
plugin = waggle.plugin.PrintPlugin()

while True:
    # Add our three measurements to the batch.
    plugin.add_measurement({'sensor_id': 1, 'parameter_id': 0, 'value': 100})
    plugin.add_measurement({'sensor_id': 1, 'parameter_id': 1, 'value': 32.1})
    plugin.add_measurement({'sensor_id': 2, 'parameter_id': 0, 'value': b'blob of data'})

    # Publish the batch.
    plugin.publish_measurements()

    # Wait five seconds before repeating.
    time.sleep(5)
