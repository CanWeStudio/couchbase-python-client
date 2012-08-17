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

import time
import uuid
import warnings

from nose.plugins.attrib import attr

from couchbase.memcachedclient import MemcachedClient
from couchbase.exception import MemcachedError, MemcachedConfigurationError
from couchbase.tests.base import Base


class MemcachedClientTest(Base):
    def setUp(self):
        super(MemcachedClientTest, self).setUp()
        # TODO: pull memcached port from config
        self.client = MemcachedClient(self.host)

    def tearDown(self):
        self.client.flush()

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
    def test_version(self):
        self.assertIsInstance(self.client.version()[2], str)

    @attr(cbv="1.0.0")
    def test_sasl_mechanisms(self):
        try:
            # testing for SASL enabled Memcached servers
            self.assertIsInstance(self.client.sasl_mechanisms(), frozenset)
        except MemcachedConfigurationError:
            self.assertRaises(MemcachedConfigurationError,
                              self.client.sasl_mechanisms)

    @attr(cbv="1.0.0")
    def test_getMulti(self):
        for kv in [{'key1': 'value1', 'key2': 'value2'},
                   {'int1': 1, 'int2': 2}]:
            for k in kv:
                self.client.set(k, 0, 0, kv[k])

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                # Trigger a warning.
                rv = self.client.getMulti(kv.keys())
                # Verify some things
                self.assertTrue(len(w) == 1)
                self.assertTrue("deprecated" in str(w[-1].message))

            for k in kv:
                self.assertIn(k, rv)
                self.assertEqual(rv[k][2], kv[k])

    @attr(cbv="1.0.0")
    def test_get_multi(self):
        for kv in [{'key1': 'value1', 'key2': 'value2'},
                   {'int1': 1, 'int2': 2}]:
            for k in kv:
                self.client.set(k, 0, 0, kv[k])

            rv = self.client.get_multi(kv.keys())

            for k in kv:
                self.assertIn(k, rv)
                self.assertEqual(rv[k][2], kv[k])
