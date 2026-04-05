#!/usr/bin/env python3
"""
Simple HTTPS server for hosting the SharePoint MSAL authentication page.
Runs on https://localhost:8080
"""

import http.server
import ssl
import os
import sys
from pathlib import Path

# Configuration
HOST = 'localhost'
PORT = 8080
CERT_FILE = 'localhost.pem'
KEY_FILE = 'localhost-key.pem'

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler with CORS headers enabled"""

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def generate_self_signed_cert():
    """Generate a self-signed certificate for localhost"""
    print("Generating self-signed certificate for localhost...")

    try:
        import subprocess

        # Generate private key and certificate in one command
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', KEY_FILE, '-out', CERT_FILE,
            '-days', '365', '-nodes',
            '-subj', '/CN=localhost'
        ], check=True, capture_output=True)

        print(f"✓ Certificate generated: {CERT_FILE}")
        print(f"✓ Private key generated: {KEY_FILE}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to generate certificate: {e}")
        print("Error output:", e.stderr.decode())
        return False
    except FileNotFoundError:
        print("✗ OpenSSL not found. Please install OpenSSL:")
        print("  macOS: brew install openssl")
        print("  Linux: sudo apt-get install openssl")
        return False

def main():
    """Start the HTTPS server"""

    # Check if certificates exist, if not generate them
    if not (Path(CERT_FILE).exists() and Path(KEY_FILE).exists()):
        print("SSL certificates not found.")
        if not generate_self_signed_cert():
            print("\n✗ Could not generate SSL certificates.")
            print("Please generate them manually or install OpenSSL.")
            sys.exit(1)

    # Create server
    server_address = (HOST, PORT)
    httpd = http.server.HTTPServer(server_address, CORSRequestHandler)

    # Wrap with SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print("\n" + "="*60)
    print(f"🚀 HTTPS Server running on https://{HOST}:{PORT}")
    print("="*60)
    print(f"\n📄 Open this URL in your browser:")
    print(f"   https://{HOST}:{PORT}/sharepoint-auth.html")
    print(f"\n⚙️  Make sure to add this redirect URI in Azure AD:")
    print(f"   https://{HOST}:{PORT}")
    print("\n⚠️  You'll see a browser security warning because of the")
    print("   self-signed certificate. Click 'Advanced' and proceed.")
    print("\n💡 Press Ctrl+C to stop the server\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()
