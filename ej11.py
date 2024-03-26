FILENAME = 'docker-compose-dev.yaml'
SERVER = """  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      - testing_net\n
    volumes:
      - ./server/config.ini:/config.ini
"""
NETWORKS = """networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

def new_client(file, i):
    file.write(f"""  client{i}:
    container_name: client{i}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={i}
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
    volumes:
      - ./client/config.yaml:/config.yaml\n\n""")


def main(): 
    clients = input("Ingrese la cantidad de clientes: ")
    while(not clients.isdigit()):
        clients = input("Ingrese un número válido de clientes: ")
    with open(FILENAME, "w") as file:
        file.write("version: '3.9'\nname: tp0\nservices:\n")
        file.write(SERVER)
        for i in range(int(clients)):
            new_client(file, i)
        file.write(NETWORKS)

main()