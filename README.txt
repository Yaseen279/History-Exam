BEDSIDE H&P - OFFLINE APP
=========================

What is in this folder
  index.html             the whole app (all presentations, scores, signs)
  sw.js                  makes it work offline after the first visit
  manifest.webmanifest   lets the phone install it like an app
  icon-192.png, icon-512.png

OPTION 1 - Install on your phone (recommended, no APK needed)
  1. Create a free GitHub account and a new PUBLIC repository (any name, e.g. bedside-hp).
  2. Upload ALL files from this folder to the repository root (Add file > Upload files).
  3. Repository Settings > Pages > Source: "Deploy from a branch", Branch: main, folder: / (root). Save.
  4. After a minute your app is at  https://YOUR-USERNAME.github.io/bedside-hp/
  5. Open that link in Chrome on your phone, wait for it to load fully once, then
     menu (three dots) > "Install app" or "Add to Home screen".
  6. After that it opens from the home screen and works with no internet.
  Do the same on your tablet.

OPTION 2 - Real APK (for Android sideloading)
  1. Finish Option 1 so you have the https link.
  2. Go to pwabuilder.com, paste the link, press Start, then Package for Android.
  3. Download the package, install the .apk on your phone (allow "install unknown apps").
  Publishing to Google Play needs a developer account; you do not need that for personal use.

OPTION 3 - Just a file
  Copy index.html to your phone and open it in Chrome. It runs, but installing it (Option 1)
  is more reliable for keeping your saved patients.

IMPORTANT
  - Your patient log is stored inside the browser or installed app on that device only.
    It is NOT shared between phone and tablet, and clearing site data erases it.
    Use Log > Export JSON regularly, and Import JSON to move it to another device.
  - The log in the online version (claude.ai link) is separate from this offline copy.
    To bring it over: open the online app, Log > Export JSON, then in the offline app Log > Import JSON.
  - Keep patient names out. Use initials or a bed number.
  - If you update the app later, replace the files in the repository and change VERSION in sw.js
    (for example bhp-v2) so phones pick up the new version.
