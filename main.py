import os
import json
import base64
import secrets
import threading
from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_FILE = "users.json"

# Ensure the JSON file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": {}}, f, indent=4)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print("[*] Committing...")
    os.system('git config --global user.name "github-actions[bot]"')
    os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
    os.system('git add .')
    os.system('git commit -m "Automated commit after running server" || echo "No changes to commit"')
    os.system("git push origin HEAD:main")


def generate_credentials():
    return base64.urlsafe_b64encode(secrets.token_bytes(4)).decode("utf-8")

@app.route("/create", methods=["POST"])
def create_account():
    data = load_data()
    username = generate_credentials()
    password = generate_credentials()
    if username not in data["users"]:
        data["users"][username] = {"password": password, "balance": 0}
        save_data(data)
        return jsonify({"username": username, "password": password})
    else:
        return jsonify({"error": "Failed to create account"}), 500


@app.route("/users/<username>", methods=["GET"])
def user_api(username):
    data = load_data()
    if username not in data["users"]:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"balance": data["users"][username]["balance"]})


@app.route("/send", methods=["POST"])
def send():
    sender = request.json.get("sender")
    recipient = request.json.get("recipient")
    amount = request.json.get("amount")
    if not sender or not recipient or amount is None:
        return jsonify({"error": "Missing or invalid parameters"}), 400

    data = load_data()

    if sender not in data["users"] or recipient not in data["users"]:
        return jsonify({"error": "Sender or recipient not found"}), 404

    if data["users"][sender]["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    # Process transfer
    data["users"][sender]["balance"] -= amount
    data["users"][recipient]["balance"] += amount

    save_data(data)
    return jsonify({"message": f"Transferred {amount} Cryo from {sender} to {recipient}"})

def run_tunnel():
    os.system("ngrok http --url=poodle-relevant-alien.ngrok-free.app 80")

def run_site():
  print("Deployment Succeeded.")
  app.run(host="0.0.0.0", port=80)

if __name__ == "__main__":
  t1 = threading.Thread(target=run_tunnel)
  t2 = threading.Thread(target=run_site)

  t1.start()
  t2.start()

  t1.join()
  t2.join()
