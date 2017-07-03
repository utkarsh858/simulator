"""
@package p2psp-simulator
splitter_dbs module
"""

#from .splitter_core import Splitter_core
from .common import Common
from queue import Queue
from threading import Thread
import time
from .simulator_stuff import Simulator_stuff #as sim
from .simulator_stuff import team_socket #as sim
from .simulator_stuff import serve_socket #as sim
from .simulator_stuff import Socket #as sim

class Splitter_DBS(Simulator_stuff):
    MAX_NUMBER_OF_LOST_CHUNKS = 32
    #BUFFER_SIZE = 128
    
    def __init__(self):
        self.id = "S"
        self.alive = True
        self.chunk_number = 0
        self.peer_list = []
        self.losses = {}
        #self.tcp_socket = Simulator_stuff.TCP_SOCKETS[self.id]
        #self.udp_socket = Simulator_stuff.UDP_SOCKETS[self.id]
        self.destination_of_chunk = []
        self.buffer_size = Common.BUFFER_SIZE
        self.peer_number = 0
        self.max_number_of_chunk_loss = self.MAX_NUMBER_OF_LOST_CHUNKS
        self.number_of_monitors = 0
        self.outgoing_peer_list = []
        self.current_round = 0
        #self.peer_connection_socket = Socket(self.id)
        #Simulator_stuff.init(self.id)

        print(self.id, ": DBS initialized")

    def send_chunk(self, chunk, peer):
        #if __debug__:
        #    print("send_chunk: S -",message, self.chunk_number, "->", destination)
        
        #sim.UDP_SOCKETS[destination].put((self.id,message))
        #sim.UDP_send((message, self.id), destination)
        #Simulator_stuff.UDP_send((message, self.id), destination)
        self.sendto(chunk, peer)

    def receive_chunk(self):
        time.sleep(0.05) #bit-rate control
        #C->Chunk, L->Lost, G->Goodbye, B->Broken, P->Peer, M->Monitor, R-> Ready
        return "C"

    def handle_arrivals(self):
        while(self.alive):
            #Thread(target=self.handle_a_peer_arrival).start()
            #sock = self.peer_connection_socket.accept(Simulator_stuff.TCP_SOCKETS[self.id])
            self.handle_a_peer_arrival()
        
    def handle_a_peer_arrival(self):
        #content = self.tcp_socket.get()
        #content = Simulator_stuff.TCP_receive(self.id)
        content = self.recv()
        message = content[0]
        incoming_peer = content[1]
        print(self.id, ": acepted connection from peer", incoming_peer)
        #print(self.id, "----> message <----", message)
        if (message[1] == "M"):
            self.number_of_monitors += 1
        print(self.id, ": number of monitors", self.number_of_monitors)

        self.send_buffer_size(incoming_peer)
        self.send_the_number_of_peers(incoming_peer)
        self.send_the_list_of_peers(incoming_peer)
        print(self.id, ": waiting for outgoing peer")
        #receive_ready_for_receiving_chunks
        #check if we receive confirmation from the incoming_peer
        #m = self.tcp_socket.get()
        #m, x = Simulator_stuff.TCP_receive(incoming_peer)
        (m, x) = self.recv()
        print(self.id, ": received", m, "from", x)
        #m = self.recv()
        #while m[1] != incoming_peer:
            #self.tcp_socket.put(m)
            #m = self.tcp_socket.get()
            
        self.insert_peer(incoming_peer)
        Simulator_stuff.SIMULATOR_FEEDBACK["DRAW"].put(("O","Node","IN",incoming_peer))
        
    def send_buffer_size(self, peer):
        #sim.team_socket__sendto(self.buffer_size, self.id, peer)
        #sim.UDP_SOCKETS[peer].put(self.buffer_size)
        #sim.TCP_SOCKETS[peer].put(self.buffer_size)
        #Simulator_stuff.TCP_send(self.buffer_size, peer)
        print(self.id, ": sending buffer size =", self.buffer_size, "to", peer)
        self.send(self.buffer_size, peer)
        
    def send_the_number_of_peers(self, peer):
        #Simulator_stuff.TCP_send(self.number_of_monitors, peer)
        print(self.id, ": sending number of monitors =", self.number_of_monitors, "to", peer)
        self.send(self.number_of_monitors, peer)
        #sim.UDP_SOCKETS[peer].put(self.number_of_monitors)
        #Simulator_stuff.TCP_send(len(self.peer_list), peer)
        print(self.id, ": sending list of peers of length =", self.peer_list, "to", peer)
        self.send(len(self.peer_list), peer)
        #sim.UDP_SOCKETS[peer].put(len(self.peer_list))

    def send_the_list_of_peers(self, peer):
        #sim.UDP_SOCKETS[peer].put(self.peer_list)
        print(self.id, ": sending peer list =", self.peer_list, "to", peer)
        #Simulator_stuff.TCP_send(self.peer_list, peer)
        self.send(self.peer_list, peer)
        
    def insert_peer(self, peer):
        if peer not in self.peer_list:
            self.peer_list.append(peer)
        self.losses[peer] = 0
        print(self.id, ":", peer, "inserted in peer list")

    def increment_unsupportivity_of_peer(self, peer):
        try:
            self.losses[peer] += 1
        except KeyError:
            print(self.id, ":the unsupportive peer", peer, "does not exist!")
        else:
            print(self.id, ":", peer, "has loss", self.losses[peer], "chunks")
            if self.losses[peer] > Common.MAX_CHUNK_LOSS:
                print(peer, 'removed')
                self.remove_peer(peer)
        finally:
           pass     

    def process_lost_chunk(self, lost_chunk_number, sender):
        destination = get_losser(lost_chunk_number)
        print(self.id, ":", sender,"complains about lost chunk",lost_chunk_number)
        self.increment_unsupportivity_of_peer(destination)

    def get_lost_chunk_number(self, message):
        return message[0]

    def get_losser(self,lost_chunk_number):
        return self.destination_of_chunk[lost_chunk_number % self.buffer_size]

    def remove_peer(self, peer):
        try:
            self.peer_list.remove(peer)
            Simulator_stuff.SIMULATOR_FEEDBACK["DRAW"].put(("O","Node","OUT",peer))
        except ValueError:
            pass
        else:
            self.peer_number -= 1

        try:
            del self.losses[peer]
        except KeyError:
            pass

    def process_goodbye(self, peer):
        print(self.id,": received goodbye from", peer)
        if peer not in self.outgoing_peer_list:
            if peer in self.peer_list:
                self.outgoing_peer_list.append(peer)
                print(self.id, ": marked for deletion", peer)

    def say_goodbye(self, peer):
        goodbye = (-1,"G")
        #Simulator_stuff.UDP_SOCKETS[peer].put((goodbye, self.id))
        self.sendto(goodbye, peer)

        #print("goodbye sent to", peer)
    
    def moderate_the_team(self):
        while self.alive:
            #content = self.udp_socket.get()
            message = self.recvfrom()
            action = message[0]
            sender = message[1]

            if (sender == "SIM"):
                if (action[1] == "K"):
                    Simulator_stuff.SIMULATOR_FEEDBACK["DRAW"].put(("Bye","Bye"))
                    self.alive = False
            else:
                if (action[1] == "L"):
                    lost_chunk_number = self.get_lost_chunk_number(action)
                    self.process_lost_chunk(lost_chunk_number, sender)
                else:
                    self.process_goodbye(sender)

    def reset_counters(self):
        for i in self.losses:
            self.losses[i] /= 2

    def reset_counters_thread(self):
        while self.alive:
            self.reset_counters()
            time.sleep(Common.COUNTERS_TIMING)

    def compute_next_peer_number(self, peer):
        self.peer_number = (self.peer_number + 1) % len(self.peer_list)

    def start(self):
        Thread(target=self.run).start()
        
    def run(self):
        Thread(target=self.handle_arrivals).start()
        Thread(target=self.moderate_the_team).start()
        Thread(target=self.reset_counters_thread).start()

        while self.alive:
            chunk = self.receive_chunk()
            #print("--------------->", len(self.peer_list))
            try:
                peer = self.peer_list[self.peer_number]
                message = (self.chunk_number, chunk)
                
                self.send_chunk(message, peer)

                self.destination_of_chunk.insert(self.chunk_number % self.buffer_size, peer)
                self.chunk_number = (self.chunk_number + 1) % Common.MAX_CHUNK_NUMBER                
                self.compute_next_peer_number(peer)
            except IndexError:
                print(self.id, ": the monitor peer has died!")
                print(self.id, ": peer_list =", self.peer_list)
                print(self.id, ": peer_number =", self.peer_number)

            if self.peer_number == 0:
                Simulator_stuff.SIMULATOR_FEEDBACK["STATUS"].put(("R", self.current_round))
                Simulator_stuff.SIMULATOR_FEEDBACK["DRAW"].put(("R", self.current_round))
                Simulator_stuff.SIMULATOR_FEEDBACK["DRAW"].put(("T","M",self.number_of_monitors, self.current_round))
                Simulator_stuff.SIMULATOR_FEEDBACK["DRAW"].put(("T","P",(len(self.peer_list)-self.number_of_monitors), self.current_round))
                self.current_round += 1
                    
                for peer in self.outgoing_peer_list:
                    self.say_goodbye(peer)
                    self.remove_peer(peer)

                del self.outgoing_peer_list[:]
