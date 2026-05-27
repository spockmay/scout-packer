# Scout Packer
Scout Packer is a progressive web app (PWA) hosted by AWS Amplify with the backend consisting of a Python script running in AWS Lambda.

No data is stored in the cloud, everything is written to local storage. Thanks to the PWA capabilites the checklist can be interacted with even when there is no Internet connection.

Currently running at https://scoutpacker.com

## Running the App Locally
On Windows PowerShell change to the root directory of the app then start the connection to a private Amplify sandbox
```
aws login
npx ampx sandbox
```
You can also run the front-end locally by
```
npx serve src
```

## Key files
* `src\index.html` - this is the primary page for the app along with all the js necessary
* `src\styles.css` - all the styles for the page
* `src\sw.js` - defines the service worker responsible for offline use of the app
* `amplify\functions\gear-engine\handler.py` - this is the "backend" code for the system that generates the packing list

## Submitting a PR
If you want to create a PR, please create it against the `dev` branch. This will allow the merged code to be tested in a staging environment. When all tests there look good it can be merged into `main`.

