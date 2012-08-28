#
# Copyright 2012, Couchbase, Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import types
import warnings
import uuid
import time
import json

from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from nose.tools import nottest

from couchbase.client import Couchbase, Server, Bucket
from couchbase.couchbaseclient \
    import CouchbaseClient, VBucketAwareCouchbaseClient
from couchbase.tests.base import Base
from couchbase.exception import MemcachedError


class ServerTest(Base):
    @attr(cbv="1.0.0")
    def test_server_object_construction(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Trigger a warning.
            cb = Server(self.host + ':' + self.port, self.username,
                        self.password)
            self.assertIsInstance(cb.servers, types.ListType)
            # Verify some things
            self.assertTrue(len(w) == 1)
            self.assertTrue("deprecated" in str(w[-1].message))


class CouchbaseTest(Base):
    @nottest
    def setup_cb(self):
        self.cb = Couchbase(self.host + ':' + self.port,
                            self.username, self.password)

    @attr(cbv="1.0.0")
    def test_couchbase_object_construction(self):
        cb = Couchbase(self.host + ':' + self.port, self.username,
                       self.password)
        self.assertIsInstance(cb.servers, types.ListType)

    @attr(cbv="1.0.0")
    def test_couchbase_object_construction_without_port(self):
        if self.port != "8091":
            raise SkipTest
        cb = Couchbase(self.host, self.username, self.password)
        self.assertIsInstance(cb.servers, types.ListType)

    @attr(cbv="1.0.0")
    def test_vbucketawarecouchbaseclient_object_construction(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Trigger a warning.
            cb = VBucketAwareCouchbaseClient("http://" + self.host + ':'
                                             + self.port + "/pools/default",
                                             self.bucket_name, "")
            self.assertIsInstance(cb.servers, types.ListType)
            # Verify some things
            self.assertTrue(len(w) == 1)
            self.assertTrue("deprecated" in str(w[-1].message))

    @attr(cbv="1.0.0")
    def test_bucket(self):
        self.setup_cb()
        self.assertIsInstance(self.cb.bucket(self.bucket_name), Bucket)

    @attr(cbv="1.0.0")
    def test_buckets(self):
        self.setup_cb()
        buckets = self.cb.buckets()
        self.assertIsInstance(buckets, types.ListType)
        self.assertIsInstance(buckets[0], Bucket)

    @attr(cbv="1.0.0")
    def test_create(self):
        self.setup_cb()
        bucket_name = str(uuid.uuid4())
        bucket = self.cb.create(bucket_name)
        self.assertIsInstance(bucket, Bucket)
        exists = [b for b in self.cb.buckets() if b.name == bucket_name]
        self.assertTrue(len(exists))
        self.cb.delete(bucket_name)

    @attr(cbv="1.0.0")
    def test_delete(self):
        self.setup_cb()
        bucket_name = str(uuid.uuid4())
        bucket = self.cb.create(bucket_name)
        self.assertIsInstance(self.cb[bucket_name], Bucket)
        self.cb.delete(bucket_name)
        self.assertNotIn(bucket_name, self.cb)


class BucketTest(Base):
    def setUp(self):
        super(BucketTest, self).setUp()
        self.cb = Couchbase(self.host + ':' + self.port, self.username,
                            self.password)
        self.client = self.cb[self.bucket_name]

    @attr(cbv="1.0.0")
    def test_bucket_object_creation(self):
        cb = Couchbase(self.host + ':' + self.port, self.username,
                       self.password)
        bucket = Bucket(self.bucket_name, cb)
        self.assertIsInstance(bucket.server, Couchbase)
        self.assertIsInstance(bucket.mc_client, CouchbaseClient)

    @attr(cbv="1.0.0")
    def test_simple_add(self):
        self.client.add('key', 0, 0, 'value')
        self.assertTrue(self.client.get('key')[2] == 'value')

    @attr(cbv="1.0.0")
    def test_simple_append(self):
        self.client.set('key', 0, 0, 'value')
        self.client.append('key', 'appended')
        self.assertTrue(self.client.get('key')[2] == 'valueappended')

    @attr(cbv="1.0.0")
    def test_simple_delete(self):
        self.client.set('key', 0, 0, 'value')
        self.client.delete('key')
        self.assertRaises(MemcachedError, self.client.get, 'key')

    @attr(cbv="1.0.0")
    def test_simple_decr(self):
        self.client.set('key', 0, 0, '4')
        self.client.decr('key', 1)
        self.assertTrue(self.client.get('key')[2] == 3)
        # test again using set with an int
        self.client.set('key', 0, 0, 4)
        self.client.decr('key', 1)
        self.assertTrue(self.client.get('key')[2] == 3)

    @attr(cbv="1.0.0")
    def test_simple_incr(self):
        self.client.set('key', 0, 0, '1')
        self.client.incr('key', 1)
        self.assertTrue(self.client.get('key')[2] == 2)
        # test again using set with an int
        self.client.set('key', 0, 0, 1)
        self.client.incr('key', 1)
        self.assertTrue(self.client.get('key')[2] == 2)

    @attr(cbv="1.0.0")
    def test_simple_get(self):
        try:
            self.client.get('key')
            raise Exception('Key existed that should not have')
        except MemcachedError as e:
            if e.status != 1:
                raise e
        self.client.set('key', 0, 0, 'value')
        self.assertTrue(self.client.get('key')[2] == 'value')

    @attr(cbv="1.0.0")
    def test_simple_prepend(self):
        self.client.set('key', 0, 0, 'value')
        self.client.prepend('key', 'prepend')
        self.assertTrue(self.client.get('key')[2] == 'prependvalue')

    @attr(cbv="1.0.0")
    def test_simple_replace(self):
        self.client.set('key', 0, 0, 'value')
        self.client.replace('key', 0, 0, 'replaced')
        self.assertTrue(self.client.get('key')[2] == 'replaced')

    @attr(cbv="1.0.0")
    def test_simple_touch(self):
        self.client.set('key', 2, 0, 'value')
        self.client.touch('key', 5)
        time.sleep(3)
        self.assertTrue(self.client.get('key')[2] == 'value')

    @attr(cbv="1.0.0")
    def test_set_and_get(self):
        kvs = [(str(uuid.uuid4()), str(uuid.uuid4())) for i in range(0, 100)]
        for k, v in kvs:
            self.client.set(k, 0, 0, v)

        for k, v in kvs:
            self.client.get(k)

    @attr(cbv="1.0.0")
    def test_set_and_delete(self):
        kvs = [(str(uuid.uuid4()), str(uuid.uuid4())) for i in range(0, 100)]
        for k, v in kvs:
            self.client.set(k, 0, 0, v)
        for k, v in kvs:
            self.client.delete(k)

    @attr(cbv="1.0.0")
    def test_getl(self):
        key, value = str(uuid.uuid4()), str(uuid.uuid4())
        self.client.set(key, 0, 0, value)
        self.assertEqual(self.client.getl(key)[2], value)
        self.assertRaises(MemcachedError, self.client.set, key, 0, 0, value)

    @attr(cbv="1.0.0")
    def test_gat(self):
        key, value = str(uuid.uuid4()), str(uuid.uuid4())
        self.client.set(key, 2, 0, value)
        set_value = self.client.gat(key, 5)[2]
        self.assertTrue(set_value == value)
        time.sleep(3)
        self.assertTrue(self.client.get(key)[2] == value)

    @attr(cbv="1.0.0")
    def test_setitem(self):
        # test int
        self.client['int'] = 10
        self.assertEqual(self.client['int'][2], 10)
        # test long
        self.client['long'] = long(10)
        self.assertEqual(self.client['long'][2], long(10))
        # test string
        self.client['str'] = 'string'
        self.assertEqual(self.client['str'][2], 'string')
        # test json
        # dictionaries are serialized to JSON objects
        self.client['json'] = {'json':'obj'}
        # but come out as strings for now
        self.assertEqual(self.client['json'][2], json.dumps({'json':'obj'}))

    @attr(cbv="2.0.0")
    def test_design_docs(self):
        # set up some docs we can find
        for i in range(0, 10):
            self.client['doc' + str(i)] = {'name': 'doc' + str(i), 'num': i}

        design_doc = json.dumps({"views":
                                 {"testing":
                                  {"map":
                                   "function(doc) { emit(doc.name, doc.num); }"
                                   }
                                  }
                                 })
        rest = self.client.server._rest()
        if rest.couch_api_base is None:
            raise SkipTest
        rest.create_design_doc(self.client.name, 'test_ddoc', design_doc)
        ddocs = self.client.design_docs()
        self.assertIsInstance(ddocs, types.ListType)
        self.assertEqual(ddocs[0].keys()[0], '_design/test_ddoc')

if __name__ == "__main__":
    unittest.main()
