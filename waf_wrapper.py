import requests, json, re

class WafSolver():
  def __init__(self):
    self.session = requests.session()

  def getGokuProps(self, raw):
    self.baseUrl = re.search(r'<script\s+src="([^"]+challenge\.js)"></script>', raw).group(1).replace("/challenge.js", "").replace("token", "captcha") #not too efficient but functional
    match = re.search(r'window\.gokuProps\s*=\s*(\{.*?\});', raw, re.DOTALL)
    if match:
      gokuProps = json.loads(match.group(1))
      return gokuProps
    return None

  def getSolution(self, audio):
    r = requests.post("https://aws-waf-helper.vercel.app/getAudioSolution", json={
      "audioData":audio
    })
    solution = r.text
    return solution

  def verifyCaptcha(self, solution, data, gokuProps, locale):
    while True:
      r = self.session.post(f"{self.baseUrl}/verify", json={
        "state":{
          "iv":data["state"]["iv"],
          "payload":data["state"]["payload"],
        },
        "key":data["key"],
        "hmac_tag":data["hmac_tag"],
        "client_solution":solution,
        "metrics":{
          "solve_time_millis":1765
        },
        "goku_props":gokuProps,
        "locale":locale
      })
      if r.json()["success"] == False:
        print("failed, retry")
        data = r.json()["problem"]
        solution = self.getSolution(data["assets"]["audio"])
      else:
        print("solved")
        return r.json()["captcha_voucher"]

  def getToken(self, voucher):
    baseUrl = self.baseUrl.replace("captcha", "token")
    r = self.session.post(f"{baseUrl}/voucher", json={
      "captcha_voucher":voucher,
      "existing_token":None
    })
    return r.json()["token"]

  def solveCaptcha(self, gokuProps, domain, locale="en-us"):
    if not self.baseUrl:
      return "Extract Goku Props First."
    domain = domain.replace("www.", "").replace("https://", "").replace("/", "")
    url = f"{self.baseUrl}/problem?kind=audio&domain={domain}&locale={locale}"
    r = self.session.get(url)
    data = r.json()
    solution = self.getSolution(data["assets"]["audio"])
    voucher = self.verifyCaptcha(solution, data, gokuProps, locale)
    token = self.getToken(voucher)
    return token