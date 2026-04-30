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
