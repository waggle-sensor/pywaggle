from datetime import datetime
import json
import time


class MeasurementsFile:
    def __init__(self, filename):
        self.records = []

        with open(filename, "r") as f:
            for r in map(json.loads, f):
                # 2021-06-25T18:52:15.404690128Z
                r["timestamp"] = datetime.strptime(
                    r["timestamp"][:26], "%Y-%m-%dT%H:%M:%S.%f"
                )
                self.records.append(r)
        self.records.sort(key=lambda r: r["timestamp"])

    def play(self, nodelay=False):
        if len(self.records) == 0:
            return
        last_record = self.records[0]
        for r in self.records:
            delta = r["timestamp"] - last_record["timestamp"]
            if not nodelay:
                time.sleep(delta.total_seconds())
            yield r
            last_record = r


# MessagePlayer can take a SDR format file and replay the contents
# this will help support use cases where someone wants to inject known
# data into their plugin from a file.
# (think about name?)
# other features:
# should sort by timestamp / or leave no sort as flag?
# should be able to decide starting time
