#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import random
import socket
import json
import time


CONFIG = {"port": 8000}


class Server:
    def __init__(self, port_no=12000, debug=False):
        self.port_no = port_no
        self.debug = debug

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', self.port_no))
        self.socket.listen(45)

        print("Listening: ", self.port_no)

        self.accounts = dict()
        self.accounts = {"a": "1", "b": "1", "c": "1", "d": "1"}
        self.login_accounts = dict()
        self.players = dict()

        self.orders = list()
        self.order = 0

        self.is_start = False
        self.tries = 0

        self.target_phrase = None
        self.status = None

        self.wrong_letter_guess = None
        self.wrong_phrase_guess = None
        self.last_guess = None

        self.num_players = self.ask_num_players()
        self.listen_clients()

    def listen_clients(self):
        while True:
            client, addr = self.socket.accept()
            threading.Thread(target=self.listen, args=(client, addr)).start()

    def listen(self, client, addr):
        self.orders.append(addr)

        while True:
            data = client.recv(1024)
            data = json.loads(data)

            msg = data["msg"]
            args = data["args"]

            if msg == "exit":
                print(addr, " is closed.")
                self.orders.remove(addr)

                try:
                    username = self.login_accounts.pop(addr)
                    print("{} has left!".format(username))
                except KeyError:
                    pass

                try:
                    pid = self.players.pop(addr)
                    print("Player {} has left!".format(pid))
                except KeyError:
                    pass

                client.close()
                exit(0)
            elif msg == "guess letter":
                print(addr, " wants to guess a letter.")
                self.guess_letter(client, addr, args)
            elif msg == "guess phrase":
                print(addr, " wants to guess the phrase.")
                self.guess_phrase(client, addr, args)
            elif msg == "status":
                print(addr, " wants to learn status information.")
                self.status_info(client, addr, args)
            elif msg == "register":
                print(addr, " wants to register.")
                self.register(client, addr, args)
            elif msg == "login":
                print(addr, " wants to login.")
                self.login(client, addr, args)
            elif msg == "join":
                print(addr, " wants to join.")
                self.join_game(client, addr, args)
            elif msg == "admin":
                self.print_admin_info()
                response = "Hey admin!"
                self.send_message(client, response)
            elif msg == "is_ready":
                while (len(self.players) != self.num_players):
                    response = "not_ready"

                if not self.is_start:
                    self.start_game()
                print("Ready for playing!")
                response = "ready"
                self.send_message(client, response)
            elif msg == "is_turn":
                if self.tries >= 7:
                    response = "seven_wrong_guess"
                    self.send_message(client, response, args)
                    self.is_start = False
                    self.players = dict()
                elif self.is_start and "_" not in self.status:
                    response = "phrase_found"
                    args = [self.target_phrase]
                    self.send_message(client, response, args)
                    self.is_start = False
                    self.players = dict()
                else:
                    try:
                        response = self.players[self.orders[self.order % self.num_players]]
                        self.send_message(client, response)
                    except KeyError:
                        response = "game_over"
                        self.send_message(client, response)
                        self.is_start = False
                        self.players = dict()
            else:
                print(addr, " says: {}".format(msg))
                response = "Nice message!"
                self.send_message(client, response)

    def start_game(self):
        self.is_start = True
        self.order = 0
        self.tries = 0
        self.target_phrase = self.random_phrase()
        self.status = ["_" for c in self.target_phrase]
        print("Game started...")
        print("Target Phrase: ", self.target_phrase)
        print("Status: ", self.status)

        self.wrong_letter_guess = {addr: list() for addr in self.players}
        self.wrong_phrase_guess = {addr: list() for addr in self.players}

    def register(self, client, addr, args=list()):
        client_args = list()

        if not args:
            print("Empty username/password!")
            msg = "empty_information"
        elif args[0] in self.accounts:
            print("Already registered!")
            msg = "already_registered"
        else:
            username, pwd = args

            self.accounts[username] = pwd
            msg = "successful_register"

        self.send_message(client, msg, client_args)

    def login(self, client, addr, args=list()):
        client_args = list()

        if not args:
            print("Empty username/password!")
            msg = "empty_information"
        else:
            username, pwd = args

            if username not in self.accounts:
                msg = "not_registered"
            elif self.accounts[username] == pwd:
                msg = "successful_login"

                self.login_accounts[addr] = username
            elif self.accounts[username] != pwd:
                msg = "wrong_password"
            else:
                msg = "unknown_error"

        self.send_message(client, msg, client_args)

    def join_game(self, client, addr, args=list()):
        client_args = list()

        if addr not in self.login_accounts:
            print("User not logged in!")
            msg = "not_logged_in"
        elif addr in self.players:
            print("Already joined!")
            msg = "already_joined"
        elif self.is_start:
            print("The game is already started!")
            msg = "already_started"
        elif len(self.players) >= self.num_players:
            print("Too many players!")
            msg = "over_capacity"
        else:
            print("Successfully joined")
            pid = len(self.players) + 1
            self.players[addr] = pid
            msg = "successful_join"
            client_args = [list("Player " + str(i)
                                for i in self.players.values()),
                           pid]

        self.send_message(client, msg, client_args)

    def guess_letter(self, client, addr, args=list()):
        client_args = list()

        if not self.is_start:
            print("Game is not started!")
            msg = "not_started"
        elif self.orders[self.order % self.num_players] != addr:
            print("Wrong turn!")
            print("Correct turn: ", self.players[self.orders[
                self.order % self.num_players]])
            msg = "wrong_turn"
            client_args = [self.players[self.orders[self.order % self.num_players]]]
        elif not args or len(args[0]) > 1:
            print("Not letter!")
            msg = "not_letter"

            self.tries += 1
            self.order += 1

            self.last_guess = args[0].lower()

            if args:
                self.wrong_letter_guess[addr].append(args[0].lower())
        else:
            letter = args[0]
            num_correct = self.change_letter(letter)

            if num_correct > 0:
                msg = "correct_guess_letter"
            else:
                msg = "wrong_guess_letter"

                self.wrong_letter_guess[addr].append(letter.lower())
                self.tries += 1

            self.last_guess = letter.lower()

            self.order += 1

        self.send_message(client, msg, client_args)

    def guess_phrase(self, client, addr, args=list()):
        client_args = list()

        if not self.is_start:
            print("Game is not started!")
            msg = "not_started"
        elif self.orders[self.order % self.num_players] != addr:
            print("Wrong turn!")
            print("Correct turn: ", self.players[self.orders[
                self.order % self.num_players]])
            msg = "wrong_turn"
        else:
            phrase = args[0]

            if phrase.lower() == self.target_phrase:
                print("Correct phrase!")
                msg = "correct_guess_phrase"

                self.status = self.target_phrase
            else:
                print("Wrong phrase!")
                msg = "wrong_guess_phrase"

                self.wrong_phrase_guess[addr].append(phrase.lower())
                self.tries += 1

            self.last_guess = phrase.lower()
            self.order += 1

        self.send_message(client, msg, client_args)

    def status_info(self, client, addr, args=list()):
        client_args = list()

        if not self.is_start:
            print("Game is not started!")
            msg = "not_started"
        elif addr not in self.players:
            print(addr, " is not in the game")
            msg = "not_playing"
        else:
            print("Giving the status.")
            msg = "successful_status"

            client_args = [self.status,
                           [str(i) for i in self.players.values()],
                           self.players[self.orders[self.order % self.num_players]],
                           self.tries,
                           self.last_guess,
                           list(self.wrong_letter_guess.values()),
                           list(self.wrong_phrase_guess.values())]

        self.send_message(client, msg, client_args)

    def change_letter(self, letter):
        len_target = len(self.target_phrase)

        self.status = [letter.lower() if self.target_phrase[i] == letter.lower()
                       else self.status[i] for i in range(len_target)]

        return self.target_phrase.count(letter.lower())

    def ask_num_players(self):
        num_players = int(input("How many players?: "))

        return num_players

    def random_phrase(self, filename="phrase.txt"):
        phrase_file = open(filename, "r")
        phrases = phrase_file.read().split("\n")[:-1]

        return random.choice(phrases)

    def send_message(self, connected_socket, msg, args=list()):
        data = {
            "msg": msg,
            "args": args
        }

        data_json = json.dumps(data)

        if self.debug:
            print(data_json)

        connected_socket.send(data_json.encode())

    def print_admin_info(self):
        print("Accounts: ", self.accounts)
        print("Logged in: ", self.login_accounts)
        print("Players: ", self.players)
        print("Game started?: ", self.is_start)
        print("Target: ", self.target_phrase)
        print("Status: ", self.status)
        print("Wrong letter guess:", self.wrong_letter_guess)
        print("Wrong phrase guess:", self.wrong_phrase_guess)

    def __del__(self):
        self.socket.close()


if __name__ == "__main__":
    port_no = CONFIG["port"]
    server = Server(port_no)
