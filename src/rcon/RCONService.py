from mcipc.rcon.je import Client
from typing import List, Dict, Optional, Union, Tuple
import logging
from contextlib import contextmanager


class RCONService:
    """
    A comprehensive RCON client service for Minecraft Java Edition servers.
    
    This class provides a high-level interface to interact with Minecraft servers
    using the Remote Console (RCON) protocol through the mcipc library.
    
    :param server: The server hostname or IP address
    :type server: str
    :param port: The RCON port (default: 25575)
    :type port: int
    :param password: The RCON password
    :type password: str
    """

    def __init__(self, server: str, port: int, password: str):
        """
        Initialize the RCON service.
        
        :param server: The server hostname or IP address
        :type server: str
        :param port: The RCON port
        :type port: int
        :param password: The RCON password
        :type password: str
        """
        self.server = server
        self.port = port
        self.password = password
        self.client = None
        self._connected = False
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        Establish connection to the Minecraft server via RCON.
        
        :returns: True if connection successful, False otherwise
        :rtype: bool
        :raises: ConnectionError if connection fails
        """
        try:
            self.client = Client(self.server, self.port)
            self.client.connect()
            self.client.login(self.password)
            self._connected = True
            self.logger.info(f"Successfully connected to {self.server}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.server}:{self.port}: {e}")
            self._connected = False
            raise ConnectionError(f"Failed to connect to RCON server: {e}")

    def disconnect(self) -> None:
        """
        Disconnect from the RCON server.
        """
        if self.client and self._connected:
            try:
                self.client.close()
                self._connected = False
                self.logger.info("Disconnected from RCON server")
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")

    @contextmanager
    def connection(self):
        """
        Context manager for automatic connection handling.
        
        :yields: The RCONService instance
        
        Usage:
            with rcon_service.connection():
                players = rcon_service.get_player_list()
        """
        try:
            if not self._connected:
                self.connect()
            yield self
        finally:
            self.disconnect()

    def _ensure_connected(self) -> None:
        """
        Ensure the client is connected before executing commands.
        
        :raises: RuntimeError if not connected
        """
        if not self.client or not self._connected:
            raise RuntimeError("Not connected. Call connect() first.")

    def send_command(self, command: str) -> str:
        """
        Send a raw command to the Minecraft server.
        
        :param command: The command to send
        :type command: str
        :returns: Server response
        :rtype: str
        :raises: RuntimeError if not connected
        """
        self._ensure_connected()
        try:
            response = self.client.run(command)
            self.logger.debug(f"Command: {command} | Response: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise

    # Player Management
    def get_player_list(self) -> List[str]:
        """
        Get list of currently online players.
        
        :returns: List of player names
        :rtype: List[str]
        """
        self._ensure_connected()
        return self.client.list().players

    def get_player_count(self) -> Tuple[int, int]:
        """
        Get current and maximum player count.
        
        :returns: Tuple of (current_players, max_players)
        :rtype: Tuple[int, int]
        """
        self._ensure_connected()
        list_result = self.client.list()
        return len(list_result.players), list_result.max

    def kick_player(self, player: str, reason: str = "Kicked by admin") -> str:
        """
        Kick a player from the server.
        
        :param player: Player name to kick
        :type player: str
        :param reason: Kick reason
        :type reason: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.kick(player, reason)

    def ban_player(self, player: str, reason: str = "Banned by admin") -> str:
        """
        Ban a player from the server.
        
        :param player: Player name to ban
        :type player: str
        :param reason: Ban reason
        :type reason: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.ban(player, reason)

    def pardon_player(self, player: str) -> str:
        """
        Unban a player.
        
        :param player: Player name to unban
        :type player: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.pardon(player)

    def op_player(self, player: str) -> str:
        """
        Grant operator privileges to a player.
        
        :param player: Player name
        :type player: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.op(player)

    def deop_player(self, player: str) -> str:
        """
        Remove operator privileges from a player.
        
        :param player: Player name
        :type player: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.deop(player)

    def whitelist_add(self, player: str) -> str:
        """
        Add a player to the whitelist.
        
        :param player: Player name
        :type player: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.whitelist("add", player)

    def whitelist_remove(self, player: str) -> str:
        """
        Remove a player from the whitelist.
        
        :param player: Player name
        :type player: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.whitelist("remove", player)

    def whitelist_list(self) -> str:
        """
        List all whitelisted players.
        
        :returns: Server response with whitelist
        :rtype: str
        """
        self._ensure_connected()
        return self.client.whitelist("list")

    def whitelist_on(self) -> str:
        """
        Enable whitelist mode.
        
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.whitelist("on")

    def whitelist_off(self) -> str:
        """
        Disable whitelist mode.
        
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.whitelist("off")

    def whitelist_reload(self) -> str:
        """
        Reload the whitelist from file.
        
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.whitelist("reload")

    # Server Management
    def stop_server(self) -> str:
        """
        Stop the Minecraft server gracefully.
        
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.stop()

    def save_all(self, flush: bool = True) -> str:
        """
        Save the world to disk.
        
        :param flush: Whether to flush all pending writes
        :type flush: bool
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        command = "save-all flush" if flush else "save-all"
        return self.send_command(command)

    def save_on(self) -> str:
        """
        Enable automatic saving.
        
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command("save-on")

    def save_off(self) -> str:
        """
        Disable automatic saving.
        
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command("save-off")

    def reload_server(self) -> str:
        """
        Reload server configuration and data packs.
        
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command("reload")

    # Communication
    def broadcast_message(self, message: str) -> str:
        """
        Send a message to all players.
        
        :param message: Message to broadcast
        :type message: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.say(message)

    def tell_player(self, player: str, message: str) -> str:
        """
        Send a private message to a specific player.
        
        :param player: Target player name
        :type player: str
        :param message: Message to send
        :type message: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.tell(player, message)

    def send_title(self, player: str, title: str, subtitle: str = "") -> str:
        """
        Send a title message to a player.
        
        :param player: Target player name
        :type player: str
        :param title: Title text
        :type title: str
        :param subtitle: Subtitle text
        :type subtitle: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        if subtitle:
            return self.send_command(f'title {player} title {{"text":"{title}","color":"gold"}} {{"text":"{subtitle}","color":"yellow"}}')
        return self.send_command(f'title {player} title {{"text":"{title}","color":"gold"}}')

    # World Management
    def set_time(self, time: Union[int, str]) -> str:
        """
        Set the world time.
        
        :param time: Time value (number or 'day'/'night'/'noon'/'midnight')
        :type time: Union[int, str]
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.time("set", str(time))

    def add_time(self, time: int) -> str:
        """
        Add time to the current world time.
        
        :param time: Time to add
        :type time: int
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.time("add", str(time))

    def get_time(self) -> str:
        """
        Get current world time.
        
        :returns: Server response with current time
        :rtype: str
        """
        self._ensure_connected()
        return self.client.time("query", "gametime")

    def set_weather(self, weather: str, duration: int = 300) -> str:
        """
        Set the weather.
        
        :param weather: Weather type ('clear', 'rain', 'thunder')
        :type weather: str
        :param duration: Duration in seconds
        :type duration: int
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.weather(weather, duration)

    def set_difficulty(self, difficulty: str) -> str:
        """
        Set game difficulty.
        
        :param difficulty: Difficulty level ('peaceful', 'easy', 'normal', 'hard')
        :type difficulty: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.difficulty(difficulty)

    def set_gamemode(self, player: str, gamemode: str) -> str:
        """
        Set a player's game mode.
        
        :param player: Player name
        :type player: str
        :param gamemode: Game mode ('survival', 'creative', 'adventure', 'spectator')
        :type gamemode: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.gamemode(gamemode, player)

    def teleport_player(self, player: str, x: float, y: float, z: float) -> str:
        """
        Teleport a player to specific coordinates.
        
        :param player: Player name
        :type player: str
        :param x: X coordinate
        :type x: float
        :param y: Y coordinate
        :type y: float
        :param z: Z coordinate
        :type z: float
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.tp(player, x, y, z)

    def teleport_player_to_player(self, player: str, target: str) -> str:
        """
        Teleport a player to another player.
        
        :param player: Player to teleport
        :type player: str
        :param target: Target player
        :type target: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.tp(player, target)

    def give_item(self, player: str, item: str, count: int = 1) -> str:
        """
        Give an item to a player.
        
        :param player: Player name
        :type player: str
        :param item: Item identifier (e.g., 'minecraft:diamond')
        :type item: str
        :param count: Item count
        :type count: int
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.client.give(player, item, count)

    def clear_player_inventory(self, player: str, item: Optional[str] = None, count: Optional[int] = None) -> str:
        """
        Clear a player's inventory.
        
        :param player: Player name
        :type player: str
        :param item: Specific item to clear (optional)
        :type item: Optional[str]
        :param count: Maximum count to clear (optional)
        :type count: Optional[int]
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        if item and count:
            return self.client.clear(player, item, count)
        elif item:
            return self.client.clear(player, item)
        else:
            return self.client.clear(player)

    # Server Information
    def get_server_version(self) -> str:
        """
        Get server version information.
        
        :returns: Server response with version info
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command("version")

    def get_tps(self) -> str:
        """
        Get server performance information (TPS).
        
        :returns: Server response with TPS info
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command("tps")

    def get_seed(self) -> str:
        """
        Get the world seed.
        
        :returns: Server response with seed
        :rtype: str
        """
        self._ensure_connected()
        return self.client.seed()

    # Advanced Features
    def execute_as_player(self, player: str, command: str) -> str:
        """
        Execute a command as a specific player.
        
        :param player: Player name
        :type player: str
        :param command: Command to execute
        :type command: str
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command(f"execute as {player} run {command}")

    def set_spawn_protection(self, radius: int) -> str:
        """
        Set spawn protection radius.
        
        :param radius: Protection radius in blocks
        :type radius: int
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command(f"gamerule spawnRadius {radius}")

    def set_gamerule(self, rule: str, value: Union[str, int, bool]) -> str:
        """
        Set a game rule.
        
        :param rule: Game rule name
        :type rule: str
        :param value: Rule value
        :type value: Union[str, int, bool]
        :returns: Server response
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command(f"gamerule {rule} {str(value).lower()}")

    def get_gamerule(self, rule: str) -> str:
        """
        Get current value of a game rule.
        
        :param rule: Game rule name
        :type rule: str
        :returns: Server response with rule value
        :rtype: str
        """
        self._ensure_connected()
        return self.send_command(f"gamerule {rule}")

    def is_connected(self) -> bool:
        """
        Check if currently connected to the server.
        
        :returns: Connection status
        :rtype: bool
        """
        return self._connected and self.client is not None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __repr__(self) -> str:
        """String representation of the RCONService."""
        status = "Connected" if self._connected else "Disconnected"
        return f"RCONService({self.server}:{self.port}, {status})"


if __name__ == "__main__":
    # Example usage
    rcon_client = RCONService("127.0.0.1", 25575, "Hatsune_Miku")
    
    try:
        # Using context manager for automatic connection handling
        with rcon_client:
            print(f"Server: {rcon_client}")
            print(f"Players online: {rcon_client.get_player_list()}")
            print(f"Player count: {rcon_client.get_player_count()}")
            print(f"Server version: {rcon_client.get_server_version()}")
            
            # Example of broadcasting a message
            rcon_client.broadcast_message("Hello from RCON!")
            
            # Example of setting time to day
            rcon_client.set_time("day")
            
            # Example of saving the world
            rcon_client.save_all()
            
    except ConnectionError as e:
        print(f"Failed to connect: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")