"""
@package simulator
monitor_dbs module
"""
from queue import Queue
from .common import Common
from .peer_dbs import Peer_DBS
from .simulator_stuff import Simulator_stuff as sim

class Monitor_DBS(Peer_DBS):
    
    def __init__(self,id):
        super().__init__(id)

    def receive_buffer_size(self):
        #self.buffer_size = self.socket.get()//2
        #self.buffer_size = sim.TCP_jSOCKETS[self.id].get()//2
        #self.buffer_size = sim.TCP_receive(self.id)//2
        (self.buffer_size, sender) = self.recv()
        print(self.id,": received buffer_size =", self.buffer_size, "from", sender)
        self.buffer_size //= 2

        #--- Only for simulation purposes ----
        self.sender_of_chunks = [""]*self.buffer_size
        #-------------------------------------
        
    def say_hello(self, peer):
        hello = (-1,"H")
        #sim.UDP_SOCKETS[peer].put((hello, self.id))
        self.sendto(hello, peer)
        print(self.id, ":", hello, "sent to", peer)

    def connect_to_the_splitter(self):
        hello = (-1,"M")
        #self.splitter["socketTCP"].put((hello, self.id))
        self.connect(hello, self.splitter['id'])
        print(self.id, ":", hello, "sent to", self.splitter['id'])

    def complain(self, chunk_position):
        lost = (chunk_position,"L")
        #self.splitter["socketUDP"].put((lost, self.id))
        self.sendto(lost,  self.splitter['id'])
        print(self.id, ": lost chunk =", lost, "sent to", self.splitter['id'])

    #def PlayNextChunk (with complaints)
