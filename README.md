# sound-cloudripper

[![Python](https://img.shields.io/badge/Python-v3.11-yellow)]()

a tool whichs basically finds private soundcloud tracks by bruteforcing shareable links of on.soundcloud.com
```
Shareable soundcloud links are shrinked links, who look like this :
=> on.soundcloud.com/XXXXX => code 302 :redirect => soundcloud.com/artist/track),
and this can redirect to public tracks as well as private ones too... bruteforce time.

the script catchs the redirect, and uses a regex to find if the full link contains a private token (public ones does not have any)
and if the regex matches, then a private track has been found.

actually, because of the regex-only filter theres some false-positives:
-old private tracks who kept their same shareable link, which are public now, will stiff have a private token on the link;
-sometimes deleted tracks does match.

this is easy to fix tho, i just need to do it :')
```

---
##### Educationnal purposes only, use it at your own risk.
---

### Dependencies
use `pip install -r requirements.txt` to fulfill these

---
### CLI Arguments
- -h  |  print out the possible commands
---
- -r  |  base number of requests
- -t  |  number of simultaneous threads **(multiplies the number of requests)**
---
- -x  |  exports the positive results in a xml file (output.xml), *and updates it if it already exists.*
- -j  |  exports the positive results in a json file (output.json), *and updates it if it already exists.*
- -e  |  appends the positive results in a txt file (output.txt)
---
- -v  |  prompts positive results in real time
- -vv |  prompts positive and negative results in real time
---
- -c  | specify the soundcloud client id to ignore public/deleted tracks

---
### Usage
you can run the script without any arguments, the default values are enough for testing (25 requests, 1 thread, verbose mode).

## Features
- Keep a track record of what has been already scanned. It will skip any repeated links (you can delete the `checked.sqlite3` to restart scanning from beginning)
- JSON and XML file output containing full links grouped by artist
- CTRL+C in middle of a run saves everything that has been checked
- Retry 5 times if error occurs, then skip is still failing
- rate limit management by sleeping for given ranges of time (30 s, 1 min, 15 min, 30 min and 1 hour)

##### Example usage with arguments
```
python3 ripper.py -r 5 -t 5 -x
(run cloudripper for 25(5*5) requests, and export positive results in xml)
```
---
### why python ?
why not (i have regrets)
