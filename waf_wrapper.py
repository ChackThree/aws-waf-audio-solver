import json, re, time
from rnet import Impersonate, BlockingClient
from colorama import Fore, init

class WafSolver():
  def __init__(self, logging=True):
    self.session = BlockingClient(tls_info=True, impersonate=Impersonate.Firefox133)
    self.logging = logging
    init()

  def getGokuProps(self, raw):
    try:
      self.baseUrl = re.search(r'<script\s+src="([^"]+challenge\.js)"></script>', raw).group(1).replace("/challenge.js", "").replace("token", "captcha") #not too efficient but functional
      match = re.search(r'window\.gokuProps\s*=\s*(\{.*?\});', raw, re.DOTALL)
      if match:
        gokuProps = json.loads(match.group(1))
        return gokuProps
      return None
    except Exception as e:
      if self.logging == True:
        print(Fore.RED + f"[Solver] Fatal Error: {e}")
      return None

  def getSolution(self, assets):
    if self.solutionType == "audio":
      endpoint = "getAudioSolution"
      data = {
        "audioData":assets["audioData"]
      }
    elif self.solutionType == "visual":
      endpoint = "getVisualSolution"
      data = {
        "images":assets["images"],
        "target":assets["target"]
      }
    r = self.session.post(f"https://aws-waf-helper.vercel.app/{endpoint}", json=data)
    solution = r.json()["result"]
    return solution

  def verifyCaptcha(self, solution, gokuProps):
    data = self.rawData
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
        "locale":self.locale
      })
      response = r.json()
      if response["success"] == False:
        if self.logging == True:
          print(Fore.MAGENTA + "[Solver] Failed, retrying...")
        data = response["problem"]
        assets = self.getAssets(data=data)
        solution = self.getSolution(assets)
      else:
        if self.logging == True:
          print(Fore.MAGENTA + "[Solver] Solved...")
        return response["captcha_voucher"]

  def getToken(self, voucher):
    baseUrl = self.baseUrl.replace("captcha", "token")
    r = self.session.post(f"{baseUrl}/voucher", json={
      "captcha_voucher":voucher,
      "existing_token":None
    })
    self.end = time.perf_counter()
    return r.json()["token"]
  
  def getAssets(self, data=None):
    if self.solutionType == "audio":
      if data is None:
        url = f"{self.baseUrl}/problem?kind=audio&domain={self.domain}&locale={self.locale}"
        r = self.session.get(url)
        data = r.json()
      self.rawData = data
      audioData = data["assets"]["audio"]
      assets = {"audioData":audioData}
    elif self.solutionType == "visual":
      if data is None:
        url = f"{self.baseUrl}/problem?kind=visual&domain={self.domain}&locale={self.locale}"
        r = self.session.get(url)
        data = r.json()
      self.rawData = data
      images = json.loads(data["assets"]["images"])
      target = json.loads(data["assets"]["target"])[0]
      assets = {"images":images, "target":target}
      if self.logging == True:
        print(Fore.MAGENTA + f"[Solver] Visual Target: {target}")
    return assets

  def solveCaptcha(self, gokuProps, domain, locale="en-us", solutionType="audio", baseUrl=None):
    self.start = time.perf_counter()
    try:
      self.domain = domain.replace("www.", "").replace("https://", "").replace("/", "")
      self.locale = locale
      self.solutionType = solutionType
      if baseUrl is not None:
        self.baseUrl = baseUrl
      if self.baseUrl is None:
        if self.logging == True:
          print("[Solver] Be sure to extract Goku Props first, or manually provide both the Goku Props and the Base Url.")
        return None
      assets = self.getAssets()
      solution = self.getSolution(assets)
      if self.logging == True:
        print(Fore.MAGENTA + f"[Solver] Solution: {solution}")
      voucher = self.verifyCaptcha(solution, gokuProps)
      token = self.getToken(voucher)
      total = self.end - self.start
      if self.logging == True:
        print(Fore.MAGENTA + f"[Solver] Solved in {total:.2f}s")
      return token
    except Exception as e:
      #lazy error handling; temporary
      if self.logging == True:
        print(Fore.RED + f"[Solver] Fatal Error: {e}")
      return None
