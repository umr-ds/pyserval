import client
import rhizome

class Conversation:
    def __init__(self, my_sid, their_sid, **params):
        self.my_sid = my_sid
        self.their_sid = their_sid
        self.__dict__.update(params)
        
    def __repr__(self):
        return "Conversation(my_sid={}, their_sid={}, read={})".format(self.my_sid, self.their_sid, self.read)

    def __str__(self):
        return "MeshMS: {}* -> {}*".format(self.my_sid[:16], self.their_sid[:16])
    
class MeshMS:
    def __init__(self, _connection):
        self._connection = _connection
    
    def _sendmessage(self, their_sid, message, my_sid=None, type="text/plain", charset="utf-8"):
        if not my_sid: my_sid = self._connection.first_identity.sid

        multipart = [("message", ("message1", message, "{};charset={}".format(type, charset)))]

        request = self._connection.post("/restful/meshms/{}/{}/sendmessage".format(my_sid, their_sid), files=multipart)
        return request.text
        
    def get_conversationlist(self, my_sid=None):
        if not my_sid: my_sid = self._connection.first_identity.sid
        
        conversationlist = self._connection.get("/restful/meshms/{}/conversationlist.json".format(my_sid)).json()
        conversationlist_dict = [dict(list(zip(conversationlist["header"], conversation))) for conversation in conversationlist["rows"]]
        
        return [Conversation(**conv) for conv in conversationlist_dict]
        
        
if __name__ == "__main__":
    from pprint import pprint
    c = client.RestfulConnection(user="pum", passwd="pum123")
    
    # meshms_result = c.meshms._sendmessage("AA65B95A3817316A3FE7F96C310772699CE8E26CA07A81AD59D9D1046093AA46", "test")
    # print meshms_result
    
    convs = c.meshms.get_conversationlist()
    for conv in convs:
        print(conv)
    