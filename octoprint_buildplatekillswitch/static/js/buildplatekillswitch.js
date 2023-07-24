/*
 * View model for OctoPrint-Buildplatekillswitch
 *
 * Author: Thomas Fitzgerald
 * License: AGPLv3
 */
$(function() {
    function BuildplatekillswitchViewModel(parameters) {
        var PLUGIN_ID = "buildplatekillswitch"
        var self = this;
        self.killSwitchActive = ko.observable(false);
        self.global_settings = parameters[0];
        self.pin = ko.observable();
        self.usePullup = ko.observable();

        self.onBeforeBinding = () => {
            OctoPrint.get(`api/plugin/${PLUGIN_ID}`);
            self.settings = self.global_settings.settings.plugins[PLUGIN_ID];
            self.pin = self.settings.pin;
            self.usePullup = self.settings.usePullup;
        }

        self.onDataUpdaterPluginMessage = (plugin, data) => {
            if(data.killSwitchActive) {
                var asBool = data.killSwitchActive.toLowerCase() === 'true';
                console.debug(`killSwitchActive: ${asBool}`)
                self.killSwitchActive(asBool);
            }
        }

    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: BuildplatekillswitchViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "settingsViewModel" ],
        // Elements to bind to, e.g. #settings_plugin_buildplatekillswitch, #tab_plugin_buildplatekillswitch, ...
        elements: [ '#settings_plugin_buildplatekillswitch', '#navbar_plugin_buildplatekillswitch' ]
    });
});
