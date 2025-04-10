#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import simplejson
import time

from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
import cherrypy
from jinja2 import Environment, FileSystemLoader

# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Creates a CherryPy based web application that displays a mapbox map to let you view the current vehicle position and send the vehicle commands to fly to a particular latitude and longitude.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL is automatically started and used.")
args = parser.parse_args()

connection_string = args.connect

# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = 'udp:127.0.0.1:14550'

# Set the base path to where the HTML files are located
local_path = os.path.dirname(os.path.abspath(__file__))

# CherryPy configuration for static assets
cherrypy_conf = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': local_path
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './html/assets'
    }
}


class Drone(object):
    def __init__(self, server_enabled=True):
        self.gps_lock = False
        self.altitude = 30.0
        self.vehicle = vehicle
        self.current_coords = []
        self.webserver_enabled = server_enabled

        # Register observers
        self.vehicle.add_attribute_listener('location', self.location_callback)

    def launch(self):
        # Wait for GPS lock
        while self.vehicle.location.global_frame.lat == 0:
            time.sleep(0.1)
        self.home_coords = [self.vehicle.location.global_frame.lat,
                            self.vehicle.location.global_frame.lon]

        # Arm the vehicle and take off
        while not self.vehicle.is_armable:
            time.sleep(.1)

        self.change_mode('GUIDED')
        self.arm()
        self.takeoff()

        if self.webserver_enabled is True:
            self._run_server()

    def takeoff(self):
        self.vehicle.simple_takeoff(30.0)

    def arm(self, value=True):
        if value:
            self.vehicle.armed = True
            while not self.vehicle.armed:
                time.sleep(.1)
        else:
            self.vehicle.armed = False

    def _run_server(self):
        # Start CherryPy web server
        cherrypy.tree.mount(DroneDelivery(self), '/', config=cherrypy_conf)
        cherrypy.config.update({
            'server.socket_port': 8080,
            'server.socket_host': '0.0.0.0',
            'log.screen': None
        })
        cherrypy.engine.start()

    def change_mode(self, mode):
        self.vehicle.mode = VehicleMode(mode)
        while self.vehicle.mode.name != mode:
            time.sleep(1)

    def goto(self, location, relative=None):
        if relative:
            self.vehicle.simple_goto(
                LocationGlobalRelative(
                    float(location[0]), float(location[1]),
                    float(self.altitude)
                )
            )
        else:
            self.vehicle.simple_goto(
                LocationGlobal(
                    float(location[0]), float(location[1]),
                    float(self.altitude)
                )
            )
        self.vehicle.flush()

    def rtl(self):
        self.change_mode('RTL')

    def get_location(self):
        return [self.current_location.lat, self.current_location.lon]

    def location_callback(self, vehicle, name, location):
        if location.global_relative_frame.alt is not None:
            self.altitude = location.global_relative_frame.alt
        self.current_location = location.global_relative_frame


class DroneDelivery(object):
    def __init__(self, drone):
        self.drone = drone
        self.environment = Environment(loader=FileSystemLoader(local_path + '/html'))

    @cherrypy.expose
    def index(self):
        """Serves the homepage (index.html)."""
        template = self.environment.get_template('index.html')
        return template.render()

    @cherrypy.expose
    def command(self):
        """Serves the command page (command.html)."""
        template = self.environment.get_template('command.html')
        return template.render()

    @cherrypy.expose
    def track(self, lat=None, lon=None):
        """
        Handles the tracking page and processes POST requests from the command page.
        The drone moves to the specified coordinates (latitude, longitude).
        """
        if lat is not None and lon is not None:
            # Command to move the drone to the given latitude and longitude
            self.drone.goto([lat, lon], True)

        current_coords = self.drone.get_location()
        template = self.environment.get_template('track.html')
        return template.render(options={"current_coords": current_coords})

    @cherrypy.expose
    def rtl(self):
        """Returns the drone to the launch position."""
        self.drone.rtl()
        return "Returning to launch"


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

print('Launching Drone...')
Drone().launch()

# Block the CherryPy engine to keep it running
cherrypy.engine.block()

if not args.connect:
    # Shut down simulator if it was started.
    sitl.stop()
