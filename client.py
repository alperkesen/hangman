n#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json

CONFIG = {
    "server_name": "127.0.0.1",
    "port": 8000
}


class Client:
    def __init__(self, server_name, port_no=12000, debug=False):
        self.server_name = server_name
        self.port_no = port_no
        self.pid = -1
        self.debug = debug
        self.is_playing = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_name, self.port_no))

        self.start()

    def start(self):
        while True:
            if self.is_playing:
                print("Waiting...")

            old_pid = None

            while self.is_playing:
                msg = "is_turn"
                args = list()
                response = self.send_message(msg, args)

                if old_pid != response["msg"]:
                    self.print_status()

                old_pid = response["msg"]

                if response["msg"] == self.pid:
                    print("Your turn")
                    self.print_status()
                    break
                elif response["msg"] == "seven_wrong_guess":
                    self.is_playing = False
                    print("\n7 wrong guesses!")
                    print("Game Over\n")
                elif response["msg"] == "phrase_found":
                    self.is_playing = False
                    print("\nPhrase is found!")
                    print(response["args"][0])
                    print("Game Over\n")
                elif response["msg"] == "game_over":
                    self.is_playing = False
                    print("\nGame Over!")
                else:
                    pass

            print("\nFor help, enter 'help'")
            msg = input("Enter the message: ")
            args = list()

            if msg == "register":
                print("\n--Register--\n")

                username = input("Username: ")
                pwd = input("Password: ")
                args = [username, pwd]

                response = self.send_message(msg, args)

                if response["msg"] == "successful_register":
                    print("Successfully registered!")
                elif response["msg"] == "empty_information":
                    print("Empty username/password!")
                elif response["msg"] == "already_registered":
                    print("You have already registered!")
                else:
                    print(response)

            elif msg == "login":
                print("\n--Login--\n")

                username = input("Username: ")
                pwd = input("Password: ")
                args = [username, pwd]

                response = self.send_message(msg, args)

                if response["msg"] == "successful_login":
                    print("You have successfully logined.")
                elif response["msg"] == "wrong_password":
                    print("Wrong password.")
                elif response["msg"] == "not_registered":
                    print("Please register first.")
                elif response["msg"] == "empty_information":
                    print("Empty Username/Password!")
                else:
                    print(response)
            elif msg == "join":
                response = self.send_message(msg, args)

                if response["msg"] == "not_logged_in":
                    print("Please login")
                elif response["msg"] == "already_started":
                    print("Game is already started!")
                elif response["msg"] == "over_capacity":
                    print("Over capacity")
                elif response["msg"] == "already_joined":
                    print("You already joined the game!")
                elif response["msg"] == "successful_join":
                    print("You joined the game!")
                    other_players = response["args"][0]
                    self.pid = response["args"][1]
                    print("Current players: ", " ".join(other_players))
                    print("Waiting for other players...")

                    msg = "is_ready"
                    response = self.send_message(msg, args)

                    if response["msg"] == "ready":
                        print("Game starts!")
                    else:
                        pass

                    self.is_playing = True
                else:
                    print(response)
            elif msg == "help":
                print("\n--Commands--\n")

                print("help: print all commands")
                print("register: register player to the server")
                print("login: login to the server")
                print("join: join the game")
                print("guess letter: guess a letter for the target phrase")
                print("guess phrase: guess the phrase")
                print("exit: exit from the system")

                continue
            elif msg == "guess letter":
                letter = input("Enter the letter: ")
                args = [letter]
                response = self.send_message(msg, args)

                if response["msg"] == "not_started":
                    print("Game is not started!")
                elif response["msg"] == "wrong_turn":
                    order = response["args"][0]
                    print("It is Player {}'s turn".format(order))
                elif response["msg"] == "not_letter":
                    print("Enter only letter")
                elif response["msg"] == "correct_guess_letter":
                    print("You guessed {} letter".format(letter))
                elif response["msg"] == "wrong_guess_letter":
                    print("Wrong guess for {} letter".format(letter))
                else:
                    print(response)
            elif msg == "guess phrase":
                phrase = input("Enter the phrase: ")
                args = [phrase]
                response = self.send_message(msg, args)

                if response["msg"] == "not_started":
                    print("Game is not started!")
                elif response["msg"] == "wrong_turn":
                    order = args[0]
                    print("It is Player {}'s turn".format(order))
                elif response["msg"] == "correct_guess_phrase":
                    print("You guessed right!".format(msg))
                elif response["msg"] == "wrong_guess_phrase":
                    print("You guessed wrong!".format(msg))
                else:
                    print(response)
            elif msg == "status":
                self.print_status()
            else:
                response = self.send_message(msg, args)

            if self.debug:
                print("From server: ", response)

    def print_status(self):
        msg = "status"
        args = []

        response = self.send_message(msg, args)

        if response["msg"] == "successful_status":
            print("\nHello, Player {}!\n".format(self.pid))
            response_args = response["args"]
            status = " ".join(response_args[0])
            players = " ".join(response_args[1])
            whose_turn = "Player {}'s turn.".format(response_args[2])
            tries = response_args[3]
            last_guess = response_args[4]
            wrong_letter_guess = response_args[5]
            wrong_phrase_guess = response_args[6]

            print("Phrase: ", status)
            print()
            print("Players: ", players)
            print(whose_turn)
            print("Last guess: ", last_guess)
            print("Wrong letter guesses: ", wrong_letter_guess)
            print("Wrong phrase guesses: ", wrong_phrase_guess)
            print("Tries: ", tries)
            print("Remaining attempts: ", 7 - tries)

    def send_message(self, msg, args=list()):
        data = {
            "msg": msg,
            "args": args,
        }

        data_json = json.dumps(data)

        if self.debug:
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
