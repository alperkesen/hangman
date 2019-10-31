#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json

CONFIG = {
    "server_name": "127.0.0.1",
    "port": 8000
}


class Client:
    def __init__(self, server_name, port_no=12000):
        self.server_name = server_name
        self.port_no = port_no
        self.pid = -1

        self.register()
        self.start()

    def register(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_name, self.port_no))
        received_data = self.send_message("register")
        self.pid = received_data["msg"]

    def start(self):
        while True:
            msg = input("Enter the message: ")

            if msg == "exit":
                break

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_name, self.port_no))
            response = self.send_message(msg)
            print("From server: ", response)

    def send_message(self, msg):
        data = {
            "pid": self.pid,
            "msg": msg
        }

        data_json = json.dumps(data)
        print(data_json)
        self.socket.send(data_json.encode())

        response = json.loads(self.socket.recv(1024))

        return response

    def __del__(self):
        self.socket.close()


if __name__ == "__main__":
    server_name = CONFIG["server_name"]
    port_no = CONFIG["port"]
    client = Client(server_name, port_no)
