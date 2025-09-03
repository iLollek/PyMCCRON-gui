from mcipc.rcon.je import Client


class RCONService:
    def __init__(self, server: str, port: int, password: str):
        self.server = server
        self.port = port
        self.password = password
        self.client = None

    def connect(self):
        self.client = Client(self.server, self.port)
        self.client.connect()
        self.client.login(self.password)

    def send_command(self, command: str):
        if not self.client:
            raise RuntimeError("Not connected. Call connect() first.")
        return self.client.run(command)
    
    def get_player_list(self):
        return self.client.list().players



if __name__ == "__main__":
    rcon_client = RCONService("127.0.0.1", 25575, "Hatsune_Miku")
    rcon_client.connect()
    print(rcon_client.get_player_list())
