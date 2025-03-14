# bulk_site_creator

Simple script to bulk create sites in the Juniper Mist dashboard from CSV file.

Site information can include RF Template, Network Template and Gateway Template.

## Prerequisits:

- config.py should have the `google_api_key` value filled out as well as other values for your Mist org ( Org, API, Region )
- google_api_key should have the google maps `Geocoding` and `Timezone` APIs allowed
  - This should be set as a local envirmental variable of GOOLE_API_KEY
    - MAC = export [variable_name]=[variable_value]
    - Windows = set [variable_name]=[variable_valuie]
  - Be sure to secure your Google APi key to IP addresses
    - https://console.cloud.google.com/google/maps-apis/credentials?
- CSV with the following fields `site_name`, `site_address` with option fields `rf_template_name` and/or `spoke_template_name` and/or `network_template_name`

## Usage:

```bash
python ./site_creator.py
```

This is a fork of the Jake Synder's script that can be found at:

https://github.com/jsnyder-juniper/bulk_site_creator

### Update November 2022

Added the ability to push wan edge and network templates as part of the CSV - Fry

Added the ability to push variables for newly created site - see Roxy_Movie_Theatre.vars for format - this is a JSON file

### Currently working on (Nov 2022)

- Adding aptemplates, secpolicy, alarmtemp, and sitetemples

### Additions March 2025

- Updated config.py to also include org ID, API key, and all the URLs for the current MIST api sites


- Added a script to delete sites that you have created  - the input from this is site_created.txt
  This file is created when you run the site_creator.py script with a list of all the sites. The script will check for the name of the site and prompt you to confirm deletion.

  ```bash
  python ./delete_mist_site.py
  ```

- Added a way to check google API key as when it fails, sites are not created correctly.