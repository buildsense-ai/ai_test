#!/usr/bin/env python3
"""
AI Agent Evaluation Platform - Deployment Script
"""

import uvicorn
import socket
import sys
import os

def find_available_port(start_port: int = 8000, max_port: int = 8010) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result != 0:
                return port
        except:
            continue
    return start_port

def main():
    """Main deployment function"""
    print("🚀 Starting AI Agent Evaluation Platform...")
    
    # Find available port
    port = find_available_port()
    print(f"📡 Using port: {port}")
    
    # Check if static directory exists
    if not os.path.exists("static"):
        print("📁 Creating static directory...")
        os.makedirs("static", exist_ok=True)
    
    # Check if templates directory exists
    if not os.path.exists("templates"):
        print("❌ Error: templates directory not found!")
        sys.exit(1)
    
    try:
        # Start the server
        print(f"🌐 Server will be available at: http://localhost:{port}")
        print("🔄 Starting server...")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=False,  # Set to True for development
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 