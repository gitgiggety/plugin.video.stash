# plugin.video.stash

plugin.video.stash is an add-on for the [Kodi](https://kodi.tv) home theater
center software to incorporate [Stash](https://stashapp.cc), an organizer for
your porn. It thus allows you to view the media you have organized in Stash in
Kodi.

## Installation & Upgrades
Installation and upgrade of the plugin is managed using a custom Kodi
repository.

1. [Download](https://github.com/gitgiggety/repository.stash/releases) the
   latest release of the repository
2. When needed copy the zip file to the system Kodi is running on
3. Open Kodi
4. Enable installation of addons from unknown sources by navigating to
   *Setting/System/Add-ons* and enable *Unknown sources* and confirm
5. Open the add-on browser by navigating to *Add-ons* and select the left icon
   in the top of the navigation / sidebar
6. Select *Install from zip file*
7. Browse to the folder containing the zip file and select the file, the
   repository is now installed
8. Return to the main menu of the *Add-on Browser*
9. Select *Install from repository*
10. Select *Stash addon Repository* and continue to *Video add-ons*, *Stash Kodi
   Plugin*
11. Select *Install*

## Configuration
### Location of Stash
By default the add-on connects to http://localhost:9999. In case you enabled
https, are running Stash on a different system or port or are running in a
subdirectory you must update the base URL in the settings.

1. In Kodi-s main menu navigate to *Add-ons*
2. Navigate to the *Stash Kodi Plugin* and open the context menu (either by
   right-clicking using a mouse, long pressing using a remote, or using the
   context menu key on a keyboard)
3. Select *Settings*
4. Change the *Base URL* to where your Stash installation is running

### Authentication
In case you have enabled authentication on your Stash instance you are required
to provide the API Key to the add-on.

1. First generate the API Key in Stash by navigating to *Settings*,
   *Configuration*, *Authentication* and making sure either *API Key* is filled
   in, or use the "reload" icon to generate a new API Key and save the
   configuration
2. Return to Kodi and open the add-ons settings by navigating to *Add-ons* from
   the main menu and selecting *Settings* from the context menu of the *Stash
   Kodi Plugin*
3. Fill in the API Key as shown in Stash in the *API Key* field.

Sadly you can't copy/paste the API Key into Kodi as Kodi doesn't have clipboard
support. As an alternative you can edit the settings file manually.

1. Navigate to the [Kodi userdata directory](https://kodi.wiki/view/Userdata)
2. Open file `addon_data/plugin.video.stash/settings.xml`
3. Change line `<setting id="api_key" default="true" />` to `<setting
   id="api_key">[your API Key]</setting>`

### Disable HTTP2
If you have issues with playback feezing Kodi you need to disable HTTP2 in 
[advancedsettings.xml](https://kodi.wiki/view/Advancedsettings.xml#network).

Example advancedsettings.xml file:

```
<advancedsettings version="1.0">
    <network>
      <disablehttp2>true</disablehttp2>       
    </network>    
</advancedsettings>
```
