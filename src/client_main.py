import app_client
import sys
virtual_root_path = sys.argv[1]

app_client.Client(virtual_root_path)