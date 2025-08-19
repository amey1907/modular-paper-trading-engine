from kiteconnect import KiteConnect
import config

# Kite API credentials
api_key = config.KITE_API_KEY
api_secret = "mju9wh2k1jemo7i3sviro7rmw2krkou4"

def get_access_token(request_token):
    try:
        # Initialize Kite Connect
        kite = KiteConnect(api_key=api_key)

        # Generate session
        data = kite.generate_session(request_token, api_secret=api_secret)
        
        # Extract access token
        access_token = data["access_token"]
        
        # Set access token
        kite.set_access_token(access_token)
        
        # Fetch and print holdings
        holdings = kite.holdings()
        print("User Holdings:", holdings)
        
        # Optional: Update config.py with new access token
        with open('config.py', 'r') as file:
            config_content = file.readlines()
        
        with open('config.py', 'w') as file:
            for line in config_content:
                if line.startswith('KITE_ACCESS_TOKEN ='):
                    file.write(f'KITE_ACCESS_TOKEN = "{access_token}"\n')
                else:
                    file.write(line)
        
        print(f"\n🔑 New Access Token: {access_token}")
        print("✅ Access Token has been updated in config.py")
        
        return access_token
    
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None

# Prompt for request token
if __name__ == "__main__":
    print("🌐 Follow these steps:")
    print("1. Open this login URL in your browser:")
    kite = KiteConnect(api_key=api_key)
    print(kite.login_url())
    print("\n2. After logging in, you'll be redirected to a URL")
    print("3. Copy the 'request_token' from that URL")
    
    request_token = input("\nEnter the request_token from the callback URL: ").strip()
    
    get_access_token(request_token)
