"""SmartGrader application entry point."""

import argparse
import os
import socket
import ssl
import sys

from app import create_app


def get_lan_ip():
    """Detect the machine's LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def generate_self_signed_cert(cert_dir):
    """Generate a self-signed SSL certificate."""
    os.makedirs(cert_dir, exist_ok=True)
    cert_file = os.path.join(cert_dir, "cert.pem")
    key_file = os.path.join(cert_dir, "key.pem")

    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file

    # Use openssl command to generate cert
    os.system(
        f'openssl req -x509 -newkey rsa:2048 -keyout "{key_file}" '
        f'-out "{cert_file}" -days 365 -nodes '
        f'-subj "/CN=SmartGrader"'
    )

    if not os.path.exists(cert_file):
        print("Error: Failed to generate SSL certificate. Is OpenSSL installed?")
        sys.exit(1)

    return cert_file, key_file


def main():
    parser = argparse.ArgumentParser(description="Run SmartGrader")
    parser.add_argument("--lan", action="store_true", help="LAN mode: serve frontend + API on all interfaces")
    parser.add_argument("--ssl", action="store_true", help="Enable HTTPS with self-signed certificate (use with --lan)")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    args = parser.parse_args()

    if args.lan:
        os.environ["SERVE_STATIC"] = "true"
        os.environ.setdefault("FLASK_ENV", "production")

        # Check frontend build exists
        dist_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist", "index.html")
        if not os.path.exists(dist_dir):
            print("Error: frontend/dist/ not found. Build the frontend first:")
            print("  cd frontend && npm run build")
            sys.exit(1)

        app = create_app("production")

        lan_ip = get_lan_ip()
        protocol = "https" if args.ssl else "http"
        print(f"\n  SmartGrader LAN Mode")
        print(f"  Students can connect at: {protocol}://{lan_ip}:{args.port}")
        print(f"  Local access: {protocol}://localhost:{args.port}\n")

        ssl_context = None
        if args.ssl:
            cert_dir = os.path.join("instance", "ssl")
            cert_file, key_file = generate_self_signed_cert(cert_dir)
            ssl_context = (cert_file, key_file)
            print(f"  SSL: Using self-signed certificate (students must accept browser warning)\n")

        app.run(host="0.0.0.0", port=args.port, ssl_context=ssl_context)
    else:
        app = create_app()
        app.run(debug=True, port=args.port)


if __name__ == "__main__":
    main()
