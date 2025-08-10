## Solving using AI
- Around 90% or greater accuracy, less when using visual solutions for now.
- Currently, the solver is using my own hosted endpoint to recognize assets.
- Audio solution uses WhisperX; Visual Solution uses Google Gemini 2.5 Flash.

## Basic Usage
- Tested for HuggingFace
- Refer to waf_wrapper.py for full usage
```python
import cloudscraper
from waf_wrapper import WafSolver

session = cloudscraper.CloudScraper() # Use other bypassing client if you wish
solver = WafSolver(logging=False) # ' logging ' is "True" by default

# Send initial request to extract the gokuProps
r = session.get("https://huggingface.co/join")
gokuProps = solver.getGokuProps(r.text)

# Alternatively, If you wish to provide gokuProps without calling getGokuProps, add ' baseUrl ' as an additional argument
token = solver.solveCaptcha(gokuProps, domain="huggingface.co") # visual solving is enabled by default, to use "audio" pass arg ' solutionType="audio" '
session.headers["cookie"] = f"aws-waf-token={token}"
print(f"Solved, token: {token}")

# Send the request again, this time authenticated with token, check status
r = session.get("https://huggingface.co/join")
response = r.text
if len(response) < 3000:
  print("Blocked from HuggingFace")
elif len(response) > 3000:
  print("Allowed to access HuggingFace")
```

## Changelog
- [8/10/2025] : Added solving time for logging.
- [8/10/2025] : main.py modernized as a proper example file & supports both captcha types.
- [8/10/2025] : waf_wrapper.py now supports both audio and visual captcha solutions.
- [8/10/2025] : Changed from requests/CloudScraper to rnet for faster request speeds.
- [8/10/2025] : Changed from ``aws-waf-audio-solver`` to ``aws-waf-solver``.

## TODO
- Proxy support.
- Better error handling.
- All around faster solving time.

## Notes
- This project is still in development, if any issues arise please open a new issue in the issues tab.
- The API used to get solutions is hosted by me and open to the public completely for free, enjoy.
- Star this repo if you found it useful :)
- More features & updates will be coming soon (check TODO).

## Currently Bypassing on HuggingFace
- As seen from main.py output
<img width="528" height="229" alt="image" src="https://github.com/user-attachments/assets/7e50e873-2f20-46ca-9a0f-f418f1a28658" />
<br>
<img width="528" height="229" alt="image" src="https://github.com/user-attachments/assets/fa2b0135-c860-4802-b0d7-f2871f963bf4" />
