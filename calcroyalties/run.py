# !/bin/env python3
import logging, sys

root = logging.getLogger()
root.setLevel(logging.INFO)

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 5000

print("Starting on port:", port)

if __name__ == '__main__':
    from src.app import app

    app.run('0.0.0.0', port=port, debug=True)