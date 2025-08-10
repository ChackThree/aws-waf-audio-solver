import cloudscraper
from waf_wrapper import WafSolver

session = cloudscraper.CloudScraper()
solver = WafSolver()

r = session.get("https://huggingface.co/join")
print(r.text)
gokuProps = solver.getGokuProps(r.text)
print("Extracted Props!")
print("Attempting to solve...")
token = solver.solveCaptcha(gokuProps, "huggingface.co")
print(token)
session.headers["cookie"] = f"aws-waf-token={token}"
r = session.get("https://huggingface.co/join")
print(r.text)