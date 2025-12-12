import pygame
import pyperclip
from typing import Dict, List, Callable
from PModels import PRoom
from States.State import State
from UI.Containers import VertContainer
from UI.Label import Label
from UI.Entry import Entry
from UI.Button import TextButton
from SocketManager import SocketManager


class MainMenu(State):
    def __init__(self, game, data: object | None = None, layer="foreground"):
        super().__init__(game, data, layer)
        self.local_testing = True

        # Use SocketManager for all websocket operations
        self.socket_manager = SocketManager(local_testing=self.local_testing)

        # Thread-safe things
        self.pending_actions: List[Callable] = []

        # UI
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
            text="Join a room or create one!",
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
        """Connect to a room using SocketManager"""
        if not self.ipt_p_name.text or not self.ipt_r_id.text:
            self.res_label.set_text("Please enter both name and room ID!")
            return

        self.res_label.set_text(f"Connecting as {self.ipt_p_name.text}...")
        self.socket_manager.connect(
            self.ipt_p_name.text,
            self.ipt_r_id.text,
            on_error=lambda e: self.res_label.set_text(f"Error: {e}"),
        )

    def _on_create_clicked(self):
        """Create a room using SocketManager"""
        if not self.ipt_p_name.text:
            self.res_label.set_text("Please enter your name!")
            return

        self.res_label.set_text(f"Creating room as {self.ipt_p_name.text}...")
        self.socket_manager.create_room(
            self.ipt_p_name.text,
            on_error=lambda e: self.res_label.set_text(f"Error: {e}"),
        )

    def _on_join_queue_clicked(self):
        pass

    def update(self, delta_time):
        super().update(delta_time)

        # Execute pending actions (like pushing RoomState)
        if self.pending_actions:
            print(f"[MainMenu] Executing {len(self.pending_actions)} pending actions")
            for action in self.pending_actions:
                action()
            self.pending_actions.clear()

        # Process messages from SocketManager
        if not self.socket_manager.messages.is_empty():
            data = self.socket_manager.messages.pop()  # Use pop to consume the message
            msg_type = data.get("type")

            if msg_type == "room_not_found":
                self.res_label.set_text("Error: Room does not exist!")

            elif msg_type == "room_joined":
                self.res_label.set_text(
                    f"Joined room! Player count: {data.get('player_count')}"
                )
                # Push RoomState via pending actions to avoid threading issues
                room_data = PRoom(
                    room_id=data["room_id"],
                    host_id=data.get("host_id", ""),
                    players=data["players"],
                )
                self.pending_actions.append(
                    lambda rd=room_data: self.game.push_state(
                        RoomState(self.game, data=rd, parent_ref=self)
                    )
                )

            elif msg_type == "room_created":
                self.res_label.set_text(f"Room created! ID: {data['room_id']}")
                # Push RoomState for the newly created room
                room_data = PRoom(
                    room_id=data["room_id"],
                    host_id=data.get("host_id", self.socket_manager.player_id),
                    players=data.get("players", [self.ipt_p_name.text]),
                )
                self.pending_actions.append(
                    lambda rd=room_data: self.game.push_state(
                        RoomState(self.game, data=rd, parent_ref=self)
                    )
                )

            elif msg_type == "player_disconnected":
                print(
                    f"[MainMenu] Player disconnected. Remaining: {data.get('remaining_players')}"
                )

            elif msg_type == "connection_closed":
                self.res_label.set_text(
                    f"Connection closed: {data.get('reason', 'Unknown')}"
                )

            elif msg_type == "error":
                self.res_label.set_text(
                    f"Error: {data.get('message', 'Unknown error')}"
                )

    def render(self, surface):
        super().render(surface)


class RoomState(State):
    def __init__(
        self,
        game,
        data: PRoom = None,
        layer="foreground",
        parent_ref: MainMenu = None,
    ):
        super().__init__(game, data, layer)
        self.parent_ref = parent_ref  # Reference to MainMenu that owns the websocket
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
        self.vc_players.pack("vert")

        self.btn_start_game = None
        # Check if this player is the host using SocketManager
        if self.parent_ref.socket_manager.is_host():
            self.btn_start_game = TextButton(
                self.canvas,
                center=(self.game.SCREEN_CENTER[0], self.game.SCREEN_CENTER[1] + 20),
                text="Start game",
                command=self.start_game,
            )
            self.btn_start_game.pack()
            self.btn_start_game.toggle_interactable()

    def start_game(self):
        """Send a request to the server to start the game"""
        # Only the host can request to start the game
        print(self.parent_ref.socket_manager.player_id, self.data.host_id)
        if not self.parent_ref.socket_manager.is_host():
            print("[RoomState] Only the host can start the game!")
            return

        # Send the request to the server - server will validate and broadcast
        print("[RoomState] Requesting to start game...")
        self.parent_ref.socket_manager.send_sync(
            {"type": "start_game_request", "room_id": self.data.room_id}
        )

    def update(self, dt):
        """Check for new messages from the websocket thread"""
        super().update(dt)
        if (
            len(self.vc_players.children) == 2
            and self.btn_start_game
            and not self.btn_start_game.interactable
        ):
            self.btn_start_game.interactable = True
        elif (
            len(self.vc_players.children) < 2
            and self.btn_start_game
            and self.btn_start_game.interactable
        ):
            self.btn_start_game.interactable = False
        # Process messages from SocketManager
        if self.parent_ref and not self.parent_ref.socket_manager.messages.is_empty():
            msg = self.parent_ref.socket_manager.messages.pop()
            if msg:
                self.lab_console.set_text(str(msg))
                msg_type = msg.get("type")

                if msg_type == "room_joined":
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
                    self.vc_players.pack()
                    print(
                        f"[RoomState] Updated player list with {len(msg['players'])} players"
                    )

                elif msg_type == "player_disconnected":
                    # Remove disconnected player from the list
                    for i, c in enumerate(self.vc_players.children):
                        if c.text == msg.get("disconnected_player"):
                            self.vc_players.children.pop(i)
                            self.vc_players.pack()
                            break
                    print(
                        f"[RoomState] Player disconnected: {msg.get('disconnected_player')}"
                    )

                elif msg_type == "game_started":
                    # Server authorized the game start - transition to game state
                    print("[RoomState] Game starting!")
                    from States.GameManagerTestState import OnlineGameManagerTestState

                    self.game.push_state(
                        OnlineGameManagerTestState(
                            self.game,
                            data={
                                "socket_manager": self.parent_ref.socket_manager,
                            },
                        )
                    )

                elif msg_type == "error":
                    # Server rejected the request
                    error_msg = msg.get("message", "Unknown error")
                    print(f"[RoomState] Error from server: {error_msg}")
                    self.lab_console.set_text(f"Error: {error_msg}")

                # Log the message
                print(f"[RoomState] Received: {msg}")

    def render(self, surface):
        super().render(surface)
        pygame.draw.rect(surface, (255, 255, 255), self.vc_players.rect, 1)
