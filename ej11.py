FILENAME = 'docker-compose-dev.yaml'
TEXT = """version: '3.9'
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      - testing_net

"""
TEXT2 = """    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=1
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
      
"""
NETWORKS = """networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24"""

def main(): 
    clients = input("Ingrese la cantidad de clientes: ")
    while(not clients.isdigit()):
        clients = input("Ingrese un número válido de clientes: ")
    with open(FILENAME, "w") as file:
        file.write(TEXT)
        for i in range(int(clients)):
            file.write(f"  client{i}:\n")
            file.write(f"    container_name: client{i}\n")
            file.write(TEXT2)
        file.write(NETWORKS)

main()