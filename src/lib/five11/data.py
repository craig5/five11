# vim: set expandtab tabstop=4 shiftwidth=4 autoindent smartindent:
#
# python core
import logging
import os
import sys
# third party
#from bs4 import BeautifulSoup
import BeautifulSoup
import urllib
import yaml
# custom
import five11
import five11.constants
import five11.logger

# http://www.gtfs-data-exchange.com/agency/caltrain/
# http://511.org/developer-resources_transit-api.asp

_DATA_DIR = five11.constants._DATA_DIR

_CALTRAIN_WEEKDAY_TIMETABLE_URL = 'http://www.caltrain.com/schedules/weekdaytimetable.html'
_CALTRAIN_DATA_DIR = os.path.join(_DATA_DIR, 'caltrain')
_CALTRAIN_WEEKDAY_TIMETABLE_FILE = os.path.join(_CALTRAIN_DATA_DIR, 'weekdaytimetable.html')
_REQUIRED_NUMBER_TRAINS = 46
_REQUIRED_NUMBER_STATIONS = 29
_STATIONS_FILE = os.path.join(_DATA_DIR, 'stations.yaml')
_TRAINS_FILE = os.path.join(_DATA_DIR, 'trains.yaml')

_DEBUG_DATA_PARSE_STATIONS = False
_DEBUG_DATA_PARSE_TRAINS = False


class DataManager(object):

    def __call__(self):
        pass

    def read_train_data(self):
        self.logger.debug("Inside: {0}:{1}".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))
        with open(_TRAINS_FILE, 'r') as fp:
            self.trains_data = yaml.load(fp)

    def write_data(self):
        self.logger.debug("Inside: {0}:{1}".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))
        if not self.timetables:
            self.logger.error("Trying to write data with empty timetable.")
            # TODO throw an error when trying to write empty data
            return
        with open(_STATIONS_FILE, 'w') as fp:
            fp.write(yaml.dump(self.stations, canonical=False, default_flow_style=False))
        '''
        # Ya, it's stupid to write yaml directly.
        # But, yaml.dump() keeps crashing and I dont feel like fucking with it...
        yaml_sucks = dict()
        for direc in self.timetables.keys():
            yaml_sucks[direc] = []
            for station in self.timetables[direc]['stations']:
                yaml_station = dict()
                yaml_station['id'] = station['id']
                yaml_station['title'] = station['title']
                yaml_station['stops'] = []
                for stop in station['stops']:
                    stop_yaml = dict()
                    stop_yaml['train'] = stop['train_number']
                    #stop_yaml['time'] = stop['stop_time']
                    print stop_yaml
                    yaml_station['stops'].append(stop_yaml)
                yaml_sucks[direc].append(yaml_station)
        '''
        with open(_TRAINS_FILE, 'w') as fp:
            for direc in self.timetables.keys():
                for station in self.timetables[direc]['stations']:
                    fp.write("- station_id: {0}\n".format(station['id']))
                    fp.write("  title: {0}\n".format(station['title']))
                    fp.write("  stops:\n")
                    for stop in station['stops']:
                        fp.write("  - {0}: {1}\n".format(stop['train_number'],
                                        stop['stop_time']))

    def download_caltrain_data(self):
        self.logger.debug("Inside: {0}:{1}".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))
        sched = None
        local_file = _CALTRAIN_WEEKDAY_TIMETABLE_FILE
        if os.path.exists(local_file):
            self.logger.debug("Loading data from file: {0}".format(local_file))
            with open(local_file, 'r') as fp:
                sched = fp.read()
        else:
            url = _CALTRAIN_WEEKDAY_TIMETABLE_URL
            self.logger.debug("Loading data from URL: {0}".format(url))
            opener = urllib.FancyURLopener({})
            f = opener.open(url)
            sched = f.read()
        soup = BeautifulSoup(sched)
        return soup

    # Caltrain's site talks about an API...
    # But, after 2 attempt with no response, ripping the HTML is the only option for now.
    def fetch_caltrain(self):
        self.logger.debug("Inside: {0}:{1}".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))
        soup = self.download_caltrain_data()
        north = None
        south = None
        for table in soup.find_all('table'):
            if 'summary' in table.attrs and 'Northbound' in table.attrs['summary']:
                north = table
                continue
            if 'summary' in table.attrs and 'Southbound' in table.attrs['summary']:
                south = table
                continue
        self.timetables = dict()
        self.timetables['north'] = self.parse_caltrain_table(north)
        self.timetables['south'] = self.parse_caltrain_table(south)
        self.stations = self.calc_station_list()

    def calc_station_list(self):
        self.logger.debug("Inside: {0}:{1}".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))
        stations = dict()
        for tt in self.timetables.keys():
            self.logger.debug("Grabbing stations from timetable: {0}".format(tt))
            cur_order = 0
            for station in self.timetables[tt]['stations']:
                cur_id = station['id']
                if not cur_id in stations:
                    stations[cur_id] = dict()
                for field in ['link_path', 'title', 'zone']:
                    stations[cur_id][field] = station[field].encode('ascii', 'ignore')
                direc_order_name = "{0}_order".format(tt)
                stations[cur_id][direc_order_name] = cur_order
                cur_order += 1
        return stations

    def parse_caltrain_table(self, raw_table):
        self.logger.debug("Inside: {0}:{1}".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))
        all_rows = raw_table.tbody.find_all('tr')
        first_row = all_rows[0]
        trains = []
        for cell in first_row.find_all('th'):
            train_number = None
            if cell.string:
                train_number = cell.string[0:3]
            else:
                # The 199 cell is a huge fucking pain in the fucking ass!!
                # <th align="center" class="borderheader">199<sup>#</sup></th>
                # 'cell.string' doesn't spit out '199'
                if cell.contents and len(cell.contents) > 0:
                    train_number = cell.contents[0]
            if not train_number:
                self.logger.warn("Skipping train th: {0}".format(cell))
                continue
            # Train #199 has a trailing '#' in the string.
            # All of the rest are just 3 digits.
            if train_number.isdigit():
                new_train = {}
                # TODO add the type (bullet, limited, normal)
                # can find that by looking at the bgcolor in attrs
                new_train['number'] = train_number
                if _DEBUG_DATA_PARSE_TRAINS:
                    self.logger.debug("Found train: {0}".format(new_train))
                trains.append(new_train)
        num_trains = len(trains)
        self.logger.debug("Number of trains found: {0}".format(num_trains))
        #self.logger.debug("Number of rows in body: {0}".format(len(all_rows)))
        num_stations = len(all_rows) - 2
        self.logger.debug("Number of station rows: {0}".format(num_stations))
        if not num_stations == _REQUIRED_NUMBER_STATIONS:
            self.logger.error("Number of stations is incorrect: {0} != {1}".format(
                            num_stations, _REQUIRED_NUMBER_STATIONS))
        # First row is the header with train info.
        # Last row is the header at the bottom.
        stations = []
        for row in all_rows[1:-1]:
            ### Get the station metadata; zone, name, etc.
            all_th = row.find_all('th')
            _REQUIRED_STATION_THS = 5
            if len(all_th) != _REQUIRED_STATION_THS:
                self.logger.warn('Found station row without {0} th: {1}'.format(
                                _REQUIRED_STATION_THS, len(all_th)))
                continue
            new_station = dict()
            new_station['zone'] = all_th[0].string.strip()
            new_station['title'] = all_th[1].string.encode('ascii', 'ignore')
            href = all_th[1].find('a').attrs['href'].encode('ascii')
            new_station['link_path'] = href
            if not href.startswith('/stations') or not href.endswith('.html'):
                self.logger.warn('Bad station href: {0}'.format(href))
            station_id = href[10:-5]
            new_station['id'] = station_id
            ### Find all of the train info for this station. I.e. the time train X stops.
            tds = row.find_all('td')
            if not len(tds) == num_trains:
                self.logger.warn("Station without {0} td: {1} {2}".format(
                                num_trains, len(tds), station_id))
            new_station['stops'] = []
            cur_train_number = 0
            for stop in tds:
                cur_train = trains[cur_train_number]
                stop_time = stop.string
                if not stop_time and stop.div:
                    stop_time = stop.div.string
                if stop_time:
                    stop_time = stop_time.encode('ascii', 'ignore')
                    stop_time = stop_time.strip(' ')
                if stop_time == '-' or stop_time == '':
                    stop_time = None
                if _DEBUG_DATA_PARSE_STATIONS:
                    self.logger.debug("Stop {0} {1} '{2}'".format(station_id,
                                    cur_train['number'], stop_time))
                cur_train_number += 1
                cur_stop = {'train_number':cur_train['number'], 'stop_time':stop_time}
                new_station['stops'].append(cur_stop)
            #
            ### Add the new station to the list.
            stations.append(new_station)
            if _DEBUG_DATA_PARSE_STATIONS:
                self.logger.debug('Adding station: {0}'.format(new_station))
        self.logger.debug("Number of stations: {0}".format(len(stations)))
        if not len(stations) == _REQUIRED_NUMBER_STATIONS:
            self.logger.error("Number of stations parsed incorrect: {0} != {1}".format(
                            len(stations), _REQUIRED_NUMBER_STATIONS))
        ### Clean up the AM/PM time problem...
        # The times listed are 12-hr (not 24) and do not have any am/pm designation.
        # Need to put the times in 24-hr format.
        # Loop thru each station and make sure all hours increase.
        for station in stations:
            prev_hour = 0
            for stop in station['stops']:
                cur_time = stop['stop_time']
                # If it doesn't looking like a time, just skip it.
                if not cur_time or not ':' in cur_time:
                    continue
                cur_hour = int(cur_time[0:cur_time.find(':')])
                cur_min = cur_time[cur_time.find(':')+1:]
                if cur_hour < prev_hour:
                    cur_hour += 12
                prev_hour = cur_hour
                new_time = "{0}:{1}".format(cur_hour, cur_min)
                stop['stop_time'] = new_time
        # Loop thru every train and do the same.
        for train in trains:
            prev_hour = 0;
            train_number = train['number']
            for station in stations:
                cur_time = None
                for stop in station['stops']:
                    if stop['train_number'] == train_number:
                        cur_time = stop['stop_time']
                        break
                if not cur_time:
                    continue
                cur_hour = int(cur_time[0:cur_time.find(':')])
                cur_min = cur_time[cur_time.find(':')+1:]
                if cur_hour < prev_hour:
                    cur_hour += 12
                prev_hour = cur_hour
                new_time = "{0}:{1}".format(cur_hour, cur_min)
                for stop in station['stops']:
                    if stop['train_number'] == train_number:
                        stop['stop_time'] = new_time
        timetable = dict()
        timetable['stations'] = stations
        timetable['trains'] = trains
        return timetable


    def __init__(self, logger=None, args=None):
        if logger:
            self.logger = logger
        else:
            self.logger = five11.logger.create_logger(name=__name__)
        self.logger.debug("Logger initialized.")
        if args:
            if 'debug' in args and args.debug:
                self.logger.setLevel(logging.DEBUG)
                # This is prety brute force...
                for h in self.logger.handlers:
                    h.setLevel(logging.DEBUG)
                self.logger.debug("Resetting logging level to debug.")


class ShuttleData(object):

    def fetch_office(self, office_id):
        data_file = os.path.join(_DATA_DIR, 'shuttles.yaml')
        with open(data_file, 'r') as fp:
            yaml_data = yaml.load(fp)
        shuttles = dict()
        if office_id in yaml_data:
            shuttles = yaml_data[office_id]
        return shuttles

    def __init__(self, logger):
        self.logger = logger
# End of file.
