import os
from rnet import Impersonate, BlockingClient
from colorama import Fore, init
from waf_wrapper import WafSolver

# This a test script, for example only

os.system("cls")
init()
session = BlockingClient(
  tls_info=True, 
  impersonate=Impersonate.Firefox133
)
solver = WafSolver()

print(Fore.BLUE + f"Choose Solve Method:\n\n1. Audio Solution\n2. Visual Solution\n\n")
choice = int(input(Fore.LIGHTBLUE_EX + "$ "))

# Perform initial request, extract goku props

r = session.get("https://huggingface.co/join")
response = r.text()

if len(response) < 3000:
  print(Fore.RED + "[Main] Blocked from HuggingFace")
elif len(response) > 3000:
  print(Fore.GREEN + "[Main] Allowed to access HuggingFace")

gokuProps = solver.getGokuProps(response)
print(Fore.MAGENTA + "[Main] Extracted Props!")

# Solve the captcha according to choice

if choice == 1:
  print(Fore.MAGENTA + "[Main] Attempting to solve with Audio Solution...")
  token = solver.solveCaptcha(gokuProps, "huggingface.co", solutionType="audio")
elif choice == 2:
  print(Fore.MAGENTA + f"[Main] Attempting to solve with Visual Solution...")
  token = solver.solveCaptcha(gokuProps, "huggingface.co", solutionType="visual")

if token == None:
  print(Fore.RED + "[Main] Could not solve, exiting...")
  os._exit()

# Set the cookie

print(Fore.GREEN + f"[Main] Solved WAF: {token}")
session.update(headers={"cookie":f"aws-waf-token={token}"})

# Check if it is really solved

r = session.get("https://huggingface.co/join")
response = r.text()

if len(response) < 3000:
  print(Fore.RED + "[Main] Blocked from HuggingFace")
elif len(response) > 3000:
  print(Fore.GREEN + "[Main] Allowed to access HuggingFace")