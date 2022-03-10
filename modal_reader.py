from tkinter import Tk, LabelFrame, Entry, Button, Label

from utils import parse_args


class ModalReader:
    def __init__(self):
        self.root = Tk()

        options = parse_args()

        read_host_label = LabelFrame(text="read host")
        read_host_label.pack()
        self.read_host_entry = Entry(read_host_label)
        if options.listener_host:
            self.read_host_entry.insert(index=0, string=options.listener_host)
        self.read_host_entry.pack()

        read_port_label = LabelFrame(text="read port")
        read_port_label.pack()
        self.read_port_entry = Entry(read_port_label)
        if options.listener_port:
            self.read_port_entry.insert(index=0, string=options.listener_port)
        self.read_port_entry.pack()

        send_host_label = LabelFrame(text="send host")
        send_host_label.pack()
        self.send_host_entry = Entry(send_host_label)
        if options.send_port:
            self.send_host_entry.insert(index=0, string=options.send_host)
        self.send_host_entry.pack()

        send_port_label = LabelFrame(text="send host")
        send_port_label.pack()
        self.send_port_entry = Entry(send_port_label)
        if options.send_port:
            self.send_port_entry.insert(index=0, string=options.send_port)
        self.send_port_entry.pack()

        username_label = LabelFrame(text="username")
        username_label.pack()
        self.username_entry = Entry(username_label)
        if options.username:
            self.username_entry.insert(index=0, string=options.username)
        self.username_entry.pack()

        account_hash_label = LabelFrame(text="account_hash")
        account_hash_label.pack()
        self.account_hash_entry = Entry(account_hash_label)
        if options.token:
            self.account_hash_entry.insert(index=0, string=options.token)
        self.account_hash_entry.pack()

        Button(text="Send info", command=self.write_env).pack()
        label = Label(height=5)
        label.pack()
        self.root.mainloop()

    def write_env(self):
        with open(".txt", "w") as env_file:
            env_file.write(f"listener_host={self.read_host_entry.get()}\n")
            env_file.write(f"listener_port={self.read_port_entry.get()}\n")
            env_file.write(f"send_host={self.send_host_entry.get()}\n")
            env_file.write(f"send_port={self.send_port_entry.get()}\n")
            if self.username_entry.get():
                env_file.write(f"username={self.username_entry.get()}\n")
            if self.account_hash_entry.get():
                env_file.write(f"token={self.account_hash_entry.get()}\n")
        self.root.destroy()


if __name__ == "__main__":
    ModalReader()
