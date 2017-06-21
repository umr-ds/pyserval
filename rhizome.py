import client

class Bundle:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    @classmethod
    def from_manifest(cls, manifest):
        bundle.update_with_manifest(manifest)
        return bundle

    def update_with_manifest(self, manifest):
        pure_manifest = manifest.split("\0")[0]
        manifest_parsed = [row.split("=") for row in pure_manifest.split("\n")][:-1]
        self.__dict__.update(manifest_parsed)

    def __repr__(self):
        return "Bundle(id={}, name=\"{}\")".format(self.id, self.name)

    def __str__(self):
        if hasattr(self, "service"): prefix = self.service
        else: prefix = ""
        if hasattr(self, 'name') and self.name: 
            return "{}:{}".format(prefix, self.name)
        
        return "{}:{}*".format(prefix, self.id[:16])


class Rhizome:
    def __init__(self, _connection):
        self._connection = _connection
        
    # GET /restful/rhizome/bundlelist.json
    def get_bundlelist(self):
        bundlelist = self._connection.get("/restful/rhizome/bundlelist.json").json()
        bundlelist_dict = [dict(list(zip(bundlelist["header"], interest))) for interest in bundlelist["rows"]]
        return [Bundle(**bundle) for bundle in bundlelist_dict]

    # GET /restful/rhizome/BID.rhm
    def get_manifest(self, bid):
        manifest = self._connection.get("/restful/rhizome/{}.rhm".format(bid)).text
        return manifest.split('\0')

    # GET /restful/rhizome/BID/raw.bin
    def get_raw(self, bid):
        raw = self._connection.get("/restful/rhizome/{}/raw.bin".format(bid)).text
        return raw

    # GET /restful/rhizome/BID/decrypted.bin
    def get_decrypted(self, bid):
        decrypted = self._connection.get("/restful/rhizome/{}/decrypted.bin".format(bid)).text
        return decrypted
        
    # POST /restful/rhizome/insert
    def insert(self, bundle, payload, sid=None):
        if not sid: sid = self._connection.first_identity.sid

        manifest_file = "\n".join(["{}={}".format(x[0],x[1]) for x in bundle.__dict__.items()])+"\n"

        multipart = [("bundle-author", sid)]
        # if manifest.id: multipart.append(("bundle-id", manifest.id))
        multipart.append(("manifest", ("manifest1", manifest_file, "rhizome/manifest;format=\"text+binarysig\"")))
        multipart.append(("payload", ("file1", payload)))

        manifest_request = self._connection.post("/restful/rhizome/insert", files=multipart)
        bundle.update_with_manifest(manifest_request.text)
        return manifest_request.text
    
        

if __name__ == "__main__":
    from pprint import pprint
    c = client.RestfulConnection(user="pum", passwd="pum123")
    
    print("### Bundlelist: ")
    bundlelist = c.rhizome.get_bundlelist()
    for bundle in bundlelist:
        print(bundle)
    
    first_bundle = bundlelist[0]
    
    print("\n### Getting raw payload:")
    print(c.rhizome.get_raw(first_bundle.id))
    
    print("\n### Getting decrypted payload:")
    print(c.rhizome.get_decrypted(first_bundle.id))
    
    print("\n### Getting bundle manifest:")
    print(c.rhizome.get_manifest(first_bundle.id)[0])
    
    new = Bundle(name="PyServal Test", service="testservice")
    c.rhizome.insert(new, "Test.\n")
    print new
    
    
    