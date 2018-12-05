#!/usr/bin/env python

"""
Title: Spotify Notification Demo
Author: Stuart Colville, http://muffinresearch.co.uk
License: BSD

"""

import dbus
import sys
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
from dbus.exceptions import DBusException


class SpotifyNotifier(object):

    def __init__(self, outputType):
        """initialise."""
        self.outputType = outputType
        #bus_loop = DBusGMainLoop(set_as_default=True)
        DBusGMainLoop(set_as_default=True)
        #self.bus = dbus.SessionBus(mainloop=bus_loop)
        self.bus = dbus.SessionBus()
        loop = GObject.MainLoop()

        self.connected = False
        try:
            self.props_changed_listener()
            self.connected = True
        except DBusException as e:
            if not ("org.mpris.MediaPlayer2.spotify was not provided") in e.get_dbus_message():
                raise

        # try to get immediate output
        if (self.connected):
            properties = dbus.Interface(self.spotify, "org.freedesktop.DBus.Properties")
            if (outputType == "title"):
                metadata = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
                title = metadata.get("xesam:title")
                artist = metadata.get("xesam:artist")[0]
                print(title + "-" + artist)
            if (outputType == "status"):
                status = properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
                print(self.get_status_icon(status))

        self.session_bus = self.bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
        self.session_bus.connect_to_signal("NameOwnerChanged", self.handle_name_owner_changed, arg0="org.mpris.MediaPlayer2.spotify")

        loop.run()

    def props_changed_listener(self):
        """Hook up callback to PropertiesChanged event."""
        self.spotify = self.bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
        self.spotify.connect_to_signal("PropertiesChanged", self.handle_properties_changed)

    def handle_name_owner_changed(self, name, older_owner, new_owner):
        """Introspect the NameOwnerChanged signal to work out if spotify has started."""
        if name == "org.mpris.MediaPlayer2.spotify":
            if new_owner:
                # spotify has been launched - hook it up.
                self.props_changed_listener()
                print("Spotify started")
            else:
                self.spotify = None
                print("-")

    def handle_properties_changed(self, interface, changed_props, invalidated_props):
        """Handle track changes."""
        if (self.outputType == "status"):
            print(self.get_status_icon(changed_props.get("PlaybackStatus", {})))
        elif (self.outputType == "title"):
            print(self.get_pretty_title(changed_props.get("Metadata", {})))

    def get_status_icon(self, status):
        if status == "Playing":
            return ""
        else:
            return ""

    def get_pretty_title(self, metadata):
        title = metadata.get("xesam:title")
        #album = metadata.get("xesam:album")
        artist = metadata.get("xesam:artist")[0]
        return title + " - " + artist


def send_command(command):
    bus = dbus.SessionBus()
    connected = False
    try:
        spotify = bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
        connected = True
    except DBusException as e:
        if not ("org.mpris.MediaPlayer2.spotify was not provided") in e.get_dbus_message():
            raise
    if (connected): # connected stays True for a few seconds after spotify is closed
        if (command == "play"):
            spotify.PlayPause(dbus_interface="org.mpris.MediaPlayer2.Player")
        elif (command == "next"):
            spotify.Next(dbus_interface="org.mpris.MediaPlayer2.Player")
        elif (command == "prev"):
            spotify.Previous(dbus_interface="org.mpris.MediaPlayer2.Player")

if __name__ == "__main__":
    print("-")
    if (len(sys.argv) <= 1):
        raise ValueError("Too little arguments")
    if (sys.argv[1] in ["play", "next", "prev"]):
        send_command(sys.argv[1])
    elif (sys.argv[1] in ["title", "status"]):
        SpotifyNotifier(sys.argv[1])
    else:
        raise ValueError("Unknown argument")
