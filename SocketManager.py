import asyncio
import json
from typing import Dict, Optional, Callable
import websockets
from Collections.Stack import Stack
from Constants import get_join_room_addr, get_create_room_addr
import threading


class SocketManager:
    def __init__(self, local_testing: bool = True):
        self.local_testing = local_testing
        self.messages: Stack[Dict] = Stack(20)
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.player_id: Optional[str] = None
        self.room_id: Optional[str] = None
        self.host_id: Optional[str] = None
        self._listening = False
        self._listener_thread: Optional[threading.Thread] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None

    def connect(self, p_name: str, r_id: str, on_error: Optional[Callable] = None):
        """Start connection in a background thread"""
        if self._listening:
            print("[SocketManager] Already connected/connecting")
            return

        self._listening = True
        self._listener_thread = threading.Thread(
            target=self._run_async_connect, args=(p_name, r_id, on_error), daemon=True
        )
        self._listener_thread.start()

    def create_room(self, p_name: str, on_error: Optional[Callable] = None):
        """Start room creation in a background thread"""
        if self._listening:
            print("[SocketManager] Already connected/connecting")
            return

        self._listening = True
        self._listener_thread = threading.Thread(
            target=self._run_async_create_room, args=(p_name, on_error), daemon=True
        )
        self._listener_thread.start()

    def _run_async_connect(
        self, p_name: str, r_id: str, on_error: Optional[Callable] = None
    ):
        """Run the async connect in a new event loop (for the background thread)"""
        try:
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            self._event_loop.run_until_complete(self._connect(p_name, r_id))
        except Exception as e:
            print(f"❌ Error in _run_async_connect: {e}")
            if on_error:
                on_error(e)
        finally:
            self._listening = False
            if self._event_loop:
                self._event_loop.close()

    def _run_async_create_room(self, p_name: str, on_error: Optional[Callable] = None):
        """Run the async create_room in a new event loop (for the background thread)"""
        try:
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            self._event_loop.run_until_complete(self._create_room(p_name))
        except Exception as e:
            print(f"❌ Error in _run_async_create_room: {e}")
            if on_error:
                on_error(e)
        finally:
            self._listening = False
            if self._event_loop:
                self._event_loop.close()

    async def _connect(self, p_name: str, r_id: str):
        """Internal async method to connect and listen"""
        if not p_name or not r_id:
            raise ValueError("You have to insert a name and a room id!")

        print(f"[SocketManager] Connecting as {p_name} to room {r_id}...")
        jra = get_join_room_addr(p_name, r_id, local=self.local_testing)

        try:
            self.websocket = await websockets.connect(
                jra,
                ping_interval=20,  # Send ping every 20 seconds
                ping_timeout=10,  # Wait 10 seconds for pong
            )
            print(f"[SocketManager] Connected! Listening for messages...")

            # Continuously listen for messages
            await self._listen_loop(p_name)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ Connection closed: {e}")
            self.messages.push({"type": "connection_closed", "reason": str(e)})
        except Exception as e:
            print(f"❌ Unexpected error in _connect: {e}")
            import traceback

            traceback.print_exc()
            self.messages.push({"type": "error", "message": str(e)})

    async def _create_room(self, p_name: str):
        """Internal async method to create room and listen"""
        if not p_name:
            raise ValueError("You have to insert a name!")

        print(f"[SocketManager] Creating room as {p_name}...")
        cra = get_create_room_addr(p_name, local=self.local_testing)

        try:
            self.websocket: websockets.ClientConnection = await websockets.connect(
                cra,
                ping_interval=20,
                ping_timeout=10,
            )

            # Wait for room creation confirmation
            msg = await self.websocket.recv()
            data = json.loads(msg)
            print(f"[SocketManager] Room created: {data}")

            # Store room info
            self.room_id = data.get("room_id")
            self.host_id = data.get("player_id")  # Host is creator
            self.player_id = data.get("player_id")

            # Push the creation message
            self.messages.push(data)

            # Continue listening
            await self._listen_loop(p_name)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ Connection closed: {e}")
            self.messages.push({"type": "connection_closed", "reason": str(e)})
        except Exception as e:
            print(f"❌ Unexpected error in _create_room: {e}")
            import traceback

            traceback.print_exc()
            self.messages.push({"type": "error", "message": str(e)})

    async def _listen_loop(self, p_name: str):
        """Main listening loop - continuously receives messages"""
        while True:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)

                msg_type = data.get("type")
                print(f"[SocketManager:{p_name}] {msg_type}: {data.get('message', '')}")

                # Only set player_id ONCE when first received (don't overwrite!)
                # This prevents overwriting with other players' IDs from broadcast messages
                if "player_id" in data and self.player_id is None:
                    self.player_id = data["player_id"]
                    print(f"[SocketManager] Player ID set to: {self.player_id}")

                # Update room info if present
                if "room_id" in data:
                    self.room_id = data["room_id"]
                if "host_id" in data:
                    self.host_id = data["host_id"]

                # Store the message for game states to consume
                self.messages.push(data)

            except websockets.exceptions.ConnectionClosed:
                print(f"[SocketManager] Connection closed during listening")
                break
            except Exception as e:
                print(f"❌ Error in listen loop: {e}")
                import traceback

                traceback.print_exc()
                break

    async def send(self, data: Dict):
        """Send a message to the server"""
        if not self.websocket:
            raise RuntimeError("WebSocket is not connected")

        await self.websocket.send(json.dumps(data))
        print(f"[SocketManager] Sent: {data}")

    def send_sync(self, data: Dict):
        """Thread-safe synchronous send (schedules send in the event loop)"""
        if not self.websocket:
            print("❌ Cannot send - WebSocket is not connected")
            return

        if self._event_loop and self._event_loop.is_running():
            data["player_id"] = self.player_id
            asyncio.run_coroutine_threadsafe(self.send(data), self._event_loop)
        else:
            print("❌ Cannot send - Event loop not running")

    def disconnect(self):
        """Gracefully close the connection"""
        if self.websocket:
            if self._event_loop and self._event_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.websocket.close(), self._event_loop
                )
        self._listening = False
        print("[SocketManager] Disconnected")

    def is_connected(self) -> bool:
        """Check if the websocket is connected"""
        return self.websocket is not None

    def is_host(self) -> bool:
        """Check if the current player is the host"""
        return (
            self.player_id == self.host_id if self.player_id and self.host_id else False
        )
