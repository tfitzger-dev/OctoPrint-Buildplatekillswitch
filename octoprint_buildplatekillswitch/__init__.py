# coding=utf-8
from __future__ import absolute_import

from time import sleep

import octoprint.plugin
from gpiozero import Button

import flask

from octoprint import events

try:
    from gpiozero.pins.pigpio import PiGPIOFactory as GPIOFactory
except:
    from gpiozero.pins.mock import MockFactory as GPIOFactory


class BuildPlateKillSwitchPlugin(octoprint.plugin.SettingsPlugin,
                                 octoprint.plugin.AssetPlugin,
                                 octoprint.plugin.TemplatePlugin,
                                 octoprint.plugin.StartupPlugin,
                                 octoprint.plugin.SimpleApiPlugin,
                                 octoprint.plugin.EventHandlerPlugin
                                 ):
    PIN_LABEL = 'pin'
    USE_PULLUP_LABEL = 'usePullup'

    def __init__(self):
        super().__init__()
        self.kill_switch = None

    @property
    def pin(self):
        return self._settings.get([self.PIN_LABEL])

    @property
    def pull_up(self):
        return self._settings.get([self.USE_PULLUP_LABEL])

    def _transmit_kill_switch_status(self):
        self._plugin_manager.send_plugin_message(self._identifier, dict(killSwitchActive=f'{self.kill_switch.is_active}'))

    def update_kill_switch(self):
        self._logger.info(f'Activating Pin {self.pin} for kill switch')
        if self.kill_switch is not None:
            self.kill_switch.pin.close()
        self._logger.info(f'Pullup: {self.pull_up}')
        self.kill_switch = Button(self.pin, pull_up=self.pull_up, pin_factory=self.pin_factory)
        self.kill_switch.when_pressed = self._transmit_kill_switch_status
        self.kill_switch.when_released = self._transmit_kill_switch_status

    def on_after_startup(self, *args, **kwargs):
        try:
            self.pin_factory = GPIOFactory()
        except:
            self.pin_factory = GPIOFactory(host='octopi.local')
        self.update_kill_switch()

    def get_settings_defaults(self):
        return {
            self.PIN_LABEL: 21,
            self.USE_PULLUP_LABEL: True,
        }

    def on_settings_save(self, data):
        settings = super().on_settings_save(data)
        self.update_kill_switch()
        return settings

    def get_template_configs(self):
        return [
            {'type': 'navbar'},
            {'type': "settings"}
        ]

    def get_api_commands(self):
        return {
            'toggle': []
        }

    def on_api_command(self, command, data):
        if command == 'toggle':
            if self.kill_switch.is_active:
                self.kill_switch.pin.drive_high()
            else:
                self.kill_switch.pin.drive_low()

    def on_api_get(self, request):
        self._transmit_kill_switch_status()

    def on_event(self, event, payload):
        if event == events.Events.PRINT_STARTED:
            if not self.kill_switch.is_active:
                self._logger.info("Build plate not detected. Cancelling print")
                self._printer.cancel_print()


    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/buildplatekillswitch.js"],
            "css": ["css/buildplatekillswitch.css"],
            "less": ["less/buildplatekillswitch.less"]
        }

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "buildplatekillswitch": {
                "displayName": "Build Plate Kill Switch",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "tfitzger-dev",
                "repo": "OctoPrint-Buildplatekillswitch",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/tfitzger-dev/OctoPrint-Buildplatekillswitch/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "Build Plate Kill Switch"
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = BuildPlateKillSwitchPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
