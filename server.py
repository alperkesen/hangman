#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json

CONFIG = {"port": 8000}


class Server:
    def __init__(self, port_no=12000):
        self.port_no = port_no
        self.players = dict()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port_no))
        self.socket.listen(5)

        print("Listening: ", self.port_no)

        self.start_game()

    def start_game(self):
        self.num_players = self.ask_num_players()
        self.wait_players()
        self.listen()

    def ask_num_players(self):
        num_players = input("How many players?: ")

        return int(num_players)

    def wait_players(self):
        while len(self.players) < self.num_players:
            connected_socket, addr = self.socket.accept()
            data = connected_socket.recv(1024)
            print("From client: ", data)

            if data.pid is -1 and data.msg is "register":
                pid = len(self.players) + 1
                print("Player {} entered!".format(pid))
                sent = {"msg": pid}
                sent_json = json.dumps(sent_json)
                connected_socket.send(sent_json)
            elif data.msg is "register":
                print("Player {} is already registered!".format(data.pid))
            else:
                print("You should first register (msg is {}):", data.msg)

            connected_socket.close()

    def listen(self):
        while True:
            connected_socket, addr = self.socket.accept()
            msg = connected_socket.recv(1024)
            print("From client: ", msg)

            connected_socket.send("Nabiyon player ", msg.pid)
            connected_socket.close()


if __name__ == "__main__":
    port_no = CONFIG["port"]
    server = Server(port_no)
