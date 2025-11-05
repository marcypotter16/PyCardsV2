import asyncio
import json
import threading
import time

import pygame
import pyperclip
import websockets
from Constants import get_create_room_addr, get_join_room_addr
from PModels import PRoom
from States.State import State
from UI.Containers import VertContainer
from UI.Label import Label
from UI.Entry import Entry
from UI.Button import TextButton


class MainMenu(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, data, layer)
        self.websocket: websockets.ClientConnection = None
        self.ipt_p_name = Entry(
            self.canvas,
            center=(self.game.SCREEN_CENTER[0], self.game.SCREEN_CENTER[1] - 80),
            placeholder="Potter",
            bg_color=(50, 50, 50),
        )
        self.ipt_p_name.enter_key_callback = self._on_connect_clicked
        self.ipt_p_name.pack()

        self.ipt_r_id = Entry(
            self.canvas,
            center=(self.game.SCREEN_CENTER[0], self.game.SCREEN_CENTER[1] - 120),
            placeholder="12345678",
            bg_color=(50, 50, 50),
            height=40,
            width=200,
        )
        # self.ipt_r_id.enter_key_callback = self.btn_connect.command
        # self.ipt_r_id.pack()

        self.res_label = Label(
            self.canvas,
            center=(self.game.SCREEN_CENTER[0], self.game.SCREEN_CENTER[1] - 200),
            height=100,
            width=1000,
            fg_color=(255, 255, 255),
        )
        self.btn_connect = TextButton(
            self.canvas,
            center=self.game.SCREEN_CENTER,
            text="Connect",
            command=self._on_connect_clicked,
        )

        self.btn_connect.pack()

        self.btn_create_room = TextButton(
            self.canvas,
            center=(self.game.SCREEN_CENTER[0], self.game.SCREEN_CENTER[1] + 40),
            text="Create Room",
            command=self._on_create_clicked,
        )
        self.btn_create_room.pack()

        self.btn_enqueue = TextButton(
            self.canvas,
            center=(self.game.SCREEN_CENTER[0], self.game.SCREEN_CENTER[1] + 80),
            text="Join Queue",
            command=self._on_join_queue_clicked,
        )
        self.btn_enqueue.pack()

    def _on_connect_clicked(self):
        """Wrapper to run the async connect method in a background thread"""
        thread = threading.Thread(
            target=lambda: asyncio.run(
                self.connect(self.ipt_p_name.text, self.ipt_r_id.text)
            )
        )
        thread.daemon = True  # Thread will terminate when main program exits
        thread.start()

    def _on_create_clicked(self):
        thread = threading.Thread(
            target=lambda: asyncio.run(self.create_room_and_listen())
        )
        thread.daemon = True  # Thread will terminate when main program exits
        thread.start()

    def _on_join_queue_clicked(self):
        pass

    async def connect(self, p_name, r_id):
        if not p_name or not r_id:
            raise ValueError("You have to insert a name and a room id!")
        self.res_label.text = f"Connecting as {p_name} to room {r_id}..."
        jra = get_join_room_addr(p_name, r_id)
        self.res_label.text += f"\nJra={jra}"
        # async with websockets.connect(jra) as websocket:
        self.websocket = await websockets.connect(
            jra,
            ping_interval=20,  # Send ping every 20 seconds
            ping_timeout=10,  # Wait 10 seconds for pong
        )
        print(f"[{p_name}] Joining room {r_id}...")

        # Initialize last_message
        self.last_message = None

        # Listen for messages
        try:
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)

                msg_type = data.get("type")
                print(f"[{p_name}] {msg_type}: {data.get('message')}")

                if msg_type == "room_not_found":
                    print(f"[{p_name}] Error: Room does not exist!")
                    self.res_label.text = "Error: Room does not exist!"
                    break
                elif msg_type == "room_joined":
                    print(f"[{p_name}] Player count: {data.get('player_count')}")
                    self.res_label.text = (
                        f"[{p_name}] Player count: {data.get('player_count')}"
                    )
                    await asyncio.sleep(2)
                    self.game.push_state(
                        RoomState(
                            self.game,
                            data=PRoom(
                                room_id=data["room_id"], players=data["players"]
                            ),
                            websocket_ref=self,
                        )
                    )
                    # Continue listening after pushing RoomState
                    # Store subsequent messages for RoomState to pick up
                elif msg_type == "player_disconnected":
                    print(
                        f"[{p_name}] Remaining players: {data.get('remaining_players')}"
                    )

                # Store all messages (including heartbeats) for RoomState to process
                self.last_message = data
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ Connection closed: {e}")
            self.res_label.text = f"Disconnected: {e}"
        except Exception as e:
            print(f"❌ Unexpected error in connect: {e}")
            import traceback

            traceback.print_exc()
            self.res_label.text = f"Error: {e}"

    async def create_room_and_listen(self):
        """Create room and keep listening for messages in the same event loop"""
        if not self.ipt_p_name.text:
            raise ValueError("You have to insert a name!")
        self.res_label.text = f"Creating lobby as {self.ipt_p_name.text}"
        cra = get_create_room_addr(self.ipt_p_name.text)
        self.res_label.text += f"\nJra={cra}"

        self.websocket = await websockets.connect(
            cra,
            ping_interval=20,  # Send ping every 20 seconds
            ping_timeout=10,  # Wait 10 seconds for pong
        )

        # Wait for room creation confirmation
        msg = await self.websocket.recv()
        data = json.loads(msg)
        print(data)
        self.res_label.text = f"Created room with id: {data['room_id']}"

        # Push the RoomState but DON'T pass the websocket yet
        data["p_name"] = self.ipt_p_name.text
        data["players"] = [self.ipt_p_name.text]
        data2 = PRoom(room_id=data["room_id"], players=data["players"])
        self.game.push_state(RoomState(self.game, data=data2, websocket_ref=self))

        # Initialize last_message
        self.last_message = None

        # Now keep listening for messages in this same event loop
        try:
            while True:
                print(f"[Room {data['room_id']}] Waiting for message...")
                msg = await self.websocket.recv()
                message_data = json.loads(msg)
                print(f"[Room {data['room_id']}] Received: {message_data}")
                # Store the message for the RoomState to pick up
                self.last_message = message_data
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ Connection closed: {e}")
            self.res_label.text = f"Disconnected: {e}"
        except Exception as e:
            print(f"❌ Unexpected error in create_room_and_listen: {e}")
            import traceback

            traceback.print_exc()
            self.res_label.text = f"Error: {e}"

    def render(self, surface):
        super().render(surface)


class RoomState(State):
    def __init__(
        self, game, data: PRoom = None, layer="foreground", websocket_ref=None
    ):
        super().__init__(game, data, layer)
        self.websocket_ref = (
            websocket_ref  # Reference to MainMenu that owns the websocket
        )
        self.data = data
        # self.room_id = data.get("room_id")
        # self.p_name = data.get("p_name")

        self.lab_title = Label(
            self.canvas,
            center=(self.game.SCREEN_CENTER[0], self.game.SCREEN_CENTER[1] - 300),
            text=f"Welcome to room {self.data.room_id}",
            font=self.game.font_big,
            fg_color=(255, 255, 255),
        )
        self.btn_copy_room_id = TextButton(
            self.canvas,
            center=(self.game.SCREEN_CENTER[0], self.game.SCREEN_CENTER[1] - 20),
            text="Copy Room id",
            command=lambda: pyperclip.copy(self.data.room_id),
        )
        self.btn_copy_room_id.pack()
        self.vc_players = VertContainer(
            self.canvas,
            x=200,
            y=400,
            width=self.game.GAME_W - 400,
            height=self.game.GAME_H - 800,
        )
        self.lab_console = Label(
            self.canvas,
            x=10,
            y=600,
            width=self.game.GAME_W - 10,
            height=self.game.GAME_H - 600,
            fg_color=(255, 255, 255),
        )
        # if data.get()
        for p_id in self.data.players:

            self.vc_players.add_child(
                Label(self.vc_players, text=p_id, fg_color=(255, 255, 255))
            )

    def update(self, dt):
        """Check for new messages from the websocket thread"""
        super().update(dt)
        if self.websocket_ref and hasattr(self.websocket_ref, "last_message"):
            msg = self.websocket_ref.last_message
            if msg:
                self.lab_console.text = str(msg)
                if msg["type"] == "room_joined":
                    # Clear and rebuild player list
                    self.vc_players.clear()
                    for player_id in msg["players"]:
                        self.vc_players.add_child(
                            Label(
                                self.vc_players,
                                text=str(player_id),
                                fg_color=(255, 255, 255),
                            )
                        )
                    print(
                        f"RoomState: Updated player list with {len(msg['players'])} players"
                    )

                # Clear the message so it doesn't get processed again
                self.websocket_ref.last_message = None

                # Process the message as needed
                print(f"RoomState received: {msg}")

    def render(self, surface):
        super().render(surface)
        pygame.draw.rect(surface, (255, 255, 255), self.vc_players.rect, 1)
