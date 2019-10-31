#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json

CONFIG = {"port": 8000}


class Server:
    def __init__(self, port_no=12000):
        self.port_no = port_no
        self.players = dict()
        self.num_players = self.ask_num_players()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port_no))
        self.socket.listen(5)

        print("Listening: ", self.port_no)

        self.start_game()

    def start_game(self):
        self.wait_players()
        print("Started Game...")
        self.listen()

    def ask_num_players(self):
        num_players = int(input("How many players?: "))

        return num_players

    def wait_players(self):
        print("Waiting for players...")

        while len(self.players) < self.num_players:
            print("NumPlayers: ", self.players)
            connected_socket, addr = self.socket.accept()
            data = connected_socket.recv(1024)
            data = json.loads(data)
            print("From client: ", data, isinstance(data, dict), data["pid"], data["msg"])

            if not isinstance(data, dict):
                continue

            if data['pid'] == -1 and data['msg'] == "register":
                pid = len(self.players) + 1
                print("Player {} entered!".format(pid))
                self.players[pid] = "register"
                print(self.players)
                sent = {"msg": pid}
                sent_json = json.dumps(sent)
                connected_socket.send(sent_json.encode())
            elif data['pid'] in self.players:
                print("Player {} is already registered!".format(data["pid"]))
            else:
                print("You should first register (msg is {}):", data['msg'])

            connected_socket.close()

    def listen(self):
        while True:
            connected_socket, addr = self.socket.accept()
            data = connected_socket.recv(1024)
            data = json.loads(data)
            print("From client: ", data)

            msg = "Nabıyon player {}".format(data["pid"])
            self.send_message(msg)
            connected_socket.close()

    def send_message(self, connected_socket, msg):
        data = {
            "msg": msg
        }

        data_json = json.dumps(data)
        print(data_json)
        connected_socket.send(data_json.encode())

    def __del__(self):
        self.socket.close()


if __name__ == "__main__":
    port_no = CONFIG["port"]
    server = Server(port_no)
