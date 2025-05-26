from fyers_apiv3 import fyersModel
import yaml
import webbrowser
from pathlib import Path

CONFIG_DIR = Path("config")

def load_secrets():
    with open(CONFIG_DIR / "secrets.yaml", "r") as f:
        return yaml.safe_load(f)

def save_secrets(secrets):
    with open(CONFIG_DIR / "secrets.yaml", "w") as f:
        yaml.dump(secrets, f)

def main():
    secrets = load_secrets()
    
    # Initialize the FyersModel
    client_id = secrets["client_id"]
    secret_key = secrets["secret_key"]
    redirect_uri = secrets["redirect_uri"]
    
    # Create session model to generate token
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type="code",
        grant_type="authorization_code"
    )
    
    # Generate the auth code URL
    auth_url = session.generate_authcode()
    print("\nStep 1: Opening browser for authentication...")
    print(f"Auth URL: {auth_url}")
    webbrowser.open(auth_url)
    
    # Get the auth code from user
    print("\nStep 2: After logging in, you'll be redirected to your redirect URI")
    print("Copy the 'auth_code' parameter from the URL and paste it here:")
    auth_code = input("Auth Code: ").strip()
    
    # Generate access token
    print("\nStep 3: Generating access token...")
    session.set_token(auth_code)
    response = session.generate_token()
    
    if response["code"] != 200:
        print("Error generating token:", response)
        return
    
    # Save the access token
    access_token = response["access_token"]
    secrets["access_token"] = access_token
    save_secrets(secrets)
    
    print("\nSuccess! Access token has been saved to config/secrets.yaml")
    print("You can now run your trading system.")

if __name__ == "__main__":
    main() 