import requests
import time
import os
import resource
import hmac
import hashlib


class DiagnosticsViewerClient(object):
    def __init__(self, server, user_id=None, user_key=None, cert=True):
        """
        Create an instance of DiagnosticsViewerClient.
        """

        self.server = server
        self.id = user_id
        self.key = user_key
        self.cert = cert

    def login(self, username, password):
        credentials = requests.post(self.server + "/ea_services/credentials/%s/" % username, data={"password": password}, verify=self.cert)
        if credentials.status_code != 200:
            raise ValueError("Username/Password invalid.")

        creds = credentials.json()
        self.id = creds["id"]
        self.key = creds["key"]

        return self.id, self.key

    def upload_files(self, dataset, files):
        files_remaining = list(files)
        s = requests.Session()
        while len(files_remaining) > 0:
            total_size = 0
            files_to_send = {}
            while files_remaining and total_size < 2 * 1024 * 1024 and len(files_to_send) < resource.getrlimit(resource.RLIMIT_NOFILE)[0] / 2:
                fname = files_remaining.pop()
                files_to_send[fname] = open(fname, "rb")
                total_size += os.path.getsize(fname)

            prepped = requests.Request("POST", self.server + "/ea_services/upload/%s/" % dataset, files=files_to_send).prepare()
            h = hmac.new(self.key, prepped.body, hashlib.sha256)
            prepped.headers["X-Signature"] = h.hexdigest()
            prepped.headers["X-UserId"] = self.id

            resp = s.send(prepped, verify=self.cert)
            if resp.status_code != 200:
                raise ValueError("Failed to upload files: %s" % resp.content)
            for f in files_to_send:
                files_to_send[f].close()
            time.sleep(.01)
